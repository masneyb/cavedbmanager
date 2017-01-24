#!/bin/bash

if [ -e "${CAVEDB_WORKER_FIFO}" ] ; then
	rm "${CAVEDB_WORKER_FIFO}"
fi

FIFO_DIR=$(dirname "${CAVEDB_WORKER_FIFO}")
mkdir -p "${FIFO_DIR}"
chmod 700 "${FIFO_DIR}"

mkfifo "${CAVEDB_WORKER_FIFO}"

while [ 1 ] ; do
	BULLETIN_ID=$(cat "${CAVEDB_WORKER_FIFO}")
	if [[ ! "${BULLETIN_ID}" =~ ^[0-9]+$ ]] && [ "${BULLETIN_ID}" != "global" ]; then
		echo "Ignoring input ${BULLETIN_ID}"
		continue
	fi

	echo "Generating bulletin documents for bulletin_id ${BULLETIN_ID}"
	python /usr/local/cavedbmanager/cavedb/scripts/generate_single_bulletin.py "${BULLETIN_ID}"
done
