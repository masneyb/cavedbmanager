#!/bin/bash -u
# SPDX-License-Identifier: Apache-2.0

# This implements a very simple way to pass messages between different
# containers on the same host. Each container mounts a common worker
# volume and a message can be passed to the worker by writing an empty
# file with the message name as the filename. The worker script uses
# inotifywait to watch for new files that are written. This is so that
# the cron and web containers can notify the worker node about jobs
# that need to run. If there are multiple worker nodes in the future,
# then a proper messaging system (such as RabbitMQ) will need to be
# used, but this will work for the simple use case.

echo "Beginning to read jobs from ${CAVEDB_WORKER_MSG_DIR}"

# See if there are any queued jobs. If so, touch them so that inotify
# will pick them up.
if [ -n "$(ls -A "${CAVEDB_WORKER_MSG_DIR}")" ]; then
	(sleep 5 && find "${CAVEDB_WORKER_MSG_DIR}" -type f | head -n 1 | xargs -Iblah touch blah) &
fi

inotifywait -q --format '%f' -m "${CAVEDB_WORKER_MSG_DIR}" --event close | while read -r MSG_FILENAME ; do
	if [ "${MSG_FILENAME}" = "" ] ; then
		continue
	fi

	MSG_FULLPATH="${CAVEDB_WORKER_MSG_DIR}"/"${MSG_FILENAME}"
	if [ ! -f "${MSG_FULLPATH}" ] ; then
		continue
	fi

	echo "Beginning to process message '${MSG_FILENAME}'"

	RET=0

	if [ "${MSG_FILENAME}" == "generate:global" ] || [[ "${MSG_FILENAME}" =~ ^generate:[0-9]+$ ]] ; then
		BULLETIN_ID=${MSG_FILENAME//generate:/}
		BASE_DIR="${CAVEDB_DATA_BASE_DIR}"/bulletins/bulletin_"${BULLETIN_ID}"
		LOCK_FILE="${BASE_DIR}"/build-in-progress.lock
		BUILD_LOG="${BASE_DIR}"/bulletin-build-output.txt

		echo "Generating bulletin documents for bulletin_id ${BULLETIN_ID}"

		touch "${LOCK_FILE}"
		/usr/local/cavedbmanager/cavedb/scripts/generate_single_bulletin.py "${BULLETIN_ID}" 2>&1 | tee "${BUILD_LOG}"
		RET=$?
		rm -f "${LOCK_FILE}"
	elif [ "${MSG_FILENAME}" == "generate:all" ] ; then
		echo "Generating documents for all bulletins"

		/usr/local/cavedbmanager/cavedb/scripts/generate_all_bulletins.py
		RET=$?
	elif [ "${MSG_FILENAME}" == "elevation_dem_update" ] ; then
		echo "Updating elevations based on DEMs"

		LOG_FILE="${CAVEDB_DATA_BASE_DIR}"/elevation-dem-update.log
		/usr/local/cavedbmanager/cavedb/scripts/elevation_dem_update.py "${CAVEDB_DEM_PATH}" 2>&1 | tee "${LOG_FILE}"
		RET=$?
	elif [ "${MSG_FILENAME}" == "backup" ] ; then
		echo "Backing up data"

		HOME="${CAVEDB_DATA_BASE_DIR}" /usr/local/cavedbmanager/cavedb/scripts/backup-data.sh
		RET=$?
	else
		echo "Received unknown message ${MSG_FILENAME}"
	fi

	rm -f "${MSG_FULLPATH}"

	if [ "${RET}" != "0" ] ; then
		echo "Process returned non-zero exit status of ${RET}"
	fi

	echo "Finished processing message '${MSG_FILENAME}'"

	# Touch all messages queued (if any) since we may have a long running job and may not
	# be notified by inotifywait.
	find "${CAVEDB_WORKER_MSG_DIR}" -type f | head -n 1 | xargs -Iblah touch blah
done
