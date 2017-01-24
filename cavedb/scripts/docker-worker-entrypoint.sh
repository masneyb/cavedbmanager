#!/bin/bash

# Give PostgreSQL some time to start up
sleep 5

# Check if the database exists.
psql -lqt root | awk '{print $1}' | grep -qw "${CAVEDB_GIS_DBNAME}"
if [ "$?" != "0" ] ; then
	echo "Downloading and transforming GIS data. This may take awhile..."

	pushd /usr/local/postgis-data-importer

	mkdir -p download/us_wv download/us_wv/hillshade download/us_wv/aerial \
	         download/us_wv/aerial/USDA-2014 download/us_wv/aerial/SAMB-2003 \
	         download/us_wv/aerial/SAMB-2003/MrSID \
	         download/us_wv/aerial/SAMB-2003/JPG download/us_wv/aerial/USGS-1994 \
	         download/us_wv/dem download/us_wv/other

	patch -p1 < /usr/local/cavedbmanager/sample-bulletin/postgis-data-importer-sample-bulletin.patch

	make

	popd

	echo "Finished downloading and transforming GIS data."
fi

if [ -e "${CAVEDB_WORKER_FIFO}" ] ; then
	rm "${CAVEDB_WORKER_FIFO}"
fi

mkfifo "${CAVEDB_WORKER_FIFO}"

while [ 1 ] ; do
	BULLETIN_ID=$(cat "${CAVEDB_WORKER_FIFO}")
	if [[ ! "${BULLETIN_ID}" =~ ^[0-9]+$ ]] && [ "${BULLETIN_ID}" != "global" ]; then
		echo "Ignoring input ${BULLETIN_ID}"
		continue
	fi

	echo "Generating bulletin documents for bulletin_id ${BULLETIN_ID}"
	python ./cavedb/scripts/generate_single_bulletin.py "${BULLETIN_ID}"
done
