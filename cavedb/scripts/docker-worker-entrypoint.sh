#!/bin/bash -u
# SPDX-License-Identifier: Apache-2.0

# Give PostgreSQL some time to start up
sleep 5

# Check if the database exists.
DB=$(psql -lqt root | awk '{print $1}' | grep -w "${CAVEDB_GIS_DBNAME}")
if [ "${DB}" = "" ] ; then
	echo "Downloading and transforming GIS data. This may take awhile..."

	pushd "${POSTGIS_IMPORTER_BASE_DIR}"

	mkdir -p download/us_wv download/us_wv/hillshade download/us_wv/aerial \
	         download/us_wv/aerial/USDA-2014 download/us_wv/aerial/SAMB-2003 \
	         download/us_wv/aerial/SAMB-2003/MrSID \
	         download/us_wv/aerial/SAMB-2003/JPG download/us_wv/aerial/USGS-1994 \
	         download/us_wv/dem download/us_wv/other

	if [ "${POSTGIS_IMPORTER_SAMPLE_PATCHFILE:-}" != "" ] ; then
		patch -p1 < /usr/local/cavedbmanager/"${POSTGIS_IMPORTER_SAMPLE_PATCHFILE}"
	fi

	make

	popd

	echo "Finished downloading and transforming GIS data."
fi

chown -R www-data:www-data "${CAVEDB_DATA_BASE_DIR}"

if [ ! -d "${CAVEDB_WORKER_MSG_DIR}" ] ; then
	mkdir "${CAVEDB_WORKER_MSG_DIR}"
fi
chown -R www-data:www-data "${CAVEDB_WORKER_MSG_DIR}"
chmod 0700 "${CAVEDB_WORKER_MSG_DIR}"

gosu www-data ./cavedb/scripts/worker.sh
