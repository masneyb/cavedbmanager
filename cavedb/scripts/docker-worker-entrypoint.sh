#!/bin/bash

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

	PATCHFILE=/usr/local/cavedbmanager/sample-bulletin/postgis-data-importer-sample-bulletin.patch
	if [ -f "${PATCHFILE}" ] ; then
		patch -p1 < "${PATCHFILE}"
	fi

	make

	popd

	echo "Finished downloading and transforming GIS data."
fi

chown -R www-data:www-data /usr/local/cavedbmanager-data/

FIFO_DIR=$(dirname "${CAVEDB_WORKER_FIFO}")
if [ -d "${FIFO_DIR}" ] ; then
	chown -R www-data:www-data "${FIFO_DIR}"
fi

sudo --user www-data --preserve-env PYTHONPATH="${PYTHONPATH=}" ./cavedb/scripts/worker.sh
