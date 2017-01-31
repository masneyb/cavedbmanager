#!/bin/bash -u

# Copyright 2017 Brian Masney <masneyb@onstation.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

FIFO_DIR=$(dirname "${CAVEDB_WORKER_FIFO}")

if [ ! -d "${FIFO_DIR}" ] ; then
	mkdir -p "${FIFO_DIR}"
	chmod 0700 "${FIFO_DIR}"
fi

if [ ! -p "${CAVEDB_WORKER_FIFO}" ] ; then
	mkfifo -m 0600 "${CAVEDB_WORKER_FIFO}"
	if [ $? != 0 ] ; then
		exit 1
	fi
fi


echo "Beginning to read from fifo ${CAVEDB_WORKER_FIFO}"

while read -r MSG < "${CAVEDB_WORKER_FIFO}" ; do
	echo "Received message ${MSG}"

	if [ "${MSG}" == "generate:global" ] || [[ "${MSG}" =~ ^generate:[0-9]+$ ]] ; then
		BULLETIN_ID=${MSG//generate:/}
		BASE_DIR="${CAVEDB_DATA_BASE_DIR}"/bulletins/bulletin_"${BULLETIN_ID}"
		LOCK_FILE="${BASE_DIR}"/build-in-progress.lock
		BUILD_LOG="${BASE_DIR}"/bulletin-build-output.txt

		echo "Generating bulletin documents for bulletin_id ${BULLETIN_ID}"

		touch "${LOCK_FILE}"
		python /usr/local/cavedbmanager/cavedb/scripts/generate_single_bulletin.py "${BULLETIN_ID}" 2>&1 | tee "${BUILD_LOG}"
		rm -f "${LOCK_FILE}"
	elif [ "${MSG}" == "generate:all" ] ; then
		echo "Generating documents for all bulletins"

		python /usr/local/cavedbmanager/cavedb/scripts/generate_all_bulletins.py
	elif [ "${MSG}" == "elevation_dem_update" ] ; then
		echo "Updating elevations based on DEMs"

		LOG_FILE="${CAVEDB_DATA_BASE_DIR}"/elevation-dem-update.log
		python /usr/local/cavedbmanager/cavedb/scripts/elevation_dem_update.py "${CAVEDB_DEM_PATH}" 2>&1 | tee "${LOG_FILE}"
	elif [ "${MSG}" == "backup" ] ; then
		echo "Backing up data"

		HOME="${CAVEDB_DATA_BASE_DIR}" /usr/local/cavedbmanager/cavedb/scripts/backup-data.sh
	else
		echo "Ignoring unknown message ${MSG}"
	fi
done
