#!/bin/bash

FIFO_DIR=$(dirname "${CAVEDB_WORKER_FIFO}")

if [ -e "${CAVEDB_WORKER_FIFO}" ] ; then
	rm "${CAVEDB_WORKER_FIFO}"
elif [ ! -d "${FIFO_DIR}" ] ; then
	mkdir -p "${FIFO_DIR}"
	chmod 0700 "${FIFO_DIR}"
fi

mkfifo -m 0600 "${CAVEDB_WORKER_FIFO}"
if [ $? != 0 ] ; then
	exit 1
fi

while true ; do
	BULLETIN_ID=$(cat "${CAVEDB_WORKER_FIFO}")
	if [[ ! "${BULLETIN_ID}" =~ ^[0-9]+$ ]] && [ "${BULLETIN_ID}" != "global" ]; then
		echo "Ignoring input ${BULLETIN_ID}"
		continue
	fi

	echo "Generating bulletin documents for bulletin_id ${BULLETIN_ID}"
	python /usr/local/cavedbmanager/cavedb/scripts/generate_single_bulletin.py "${BULLETIN_ID}"
done
