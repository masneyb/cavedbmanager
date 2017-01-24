#!/bin/bash

# See if the GIS data needs to be seeded. Depending on the speed of your
# computer, this can take 15 minutes or so to complete.
NUM_DOWNLOADS=$(find /usr/local/postgis-data-importer/download/ -type f | grep -vw .placeholder | wc -l)
if [ "${NUM_DOWNLOADS}" == "0" ] ; then
	pushd /usr/local/postgis-data-importer

	mkdir -p download/us_wv download/us_wv/hillshade download/us_wv/aerial \
	         download/us_wv/aerial/USDA-2014 download/us_wv/aerial/SAMB-2003 \
	         download/us_wv/aerial/SAMB-2003/MrSID \
	         download/us_wv/aerial/SAMB-2003/JPG download/us_wv/aerial/USGS-1994 \
	         download/us_wv/dem \ download/us_wv/other

	patch -p1 < postgis-data-importer-sample-bulletin.patch

	make

	popd
fi

if [ -e "${CAVEDB_WORKER_FIFO}" ] ; then
	rm "${CAVEDB_WORKER_FIFO}"
fi

mkfifo "${CAVEDB_WORKER_FIFO}"

while [ 1 ] ; do
	BULLETIN_ID=$(cat "${CAVEDB_WORKER_FIFO}")
	if [[ ! "${BULLETIN_ID}" =~ ^[0-9]+$ ]] ; then
		echo "Ignoring input ${BULLETIN_ID}"
		continue
	fi

	echo "Generating bulletin documents for bulletin_id ${BULLETIN_ID}"
	python ./cavedb/scripts/generate_single_bulletin.py "${BULLETIN_ID}"
done
