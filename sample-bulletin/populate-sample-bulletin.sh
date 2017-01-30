#!/bin/bash -eu

# Copyright 2016-2017 Brian Masney <masneyb@onstation.org>
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

SAMPLE_DIR=$(dirname "$0")

DBNAME=cavedb
POSTGIS_DATA_IMPORTER_BASE_DIR=/usr/local/postgis-data-importer

# Create the tables in the new database. It will prompt you to create a
# Django admin user that you will use to log into the website.
python "${SAMPLE_DIR}"/../manage.py migrate auth
python "${SAMPLE_DIR}"/../manage.py migrate

if [ "${WEB_ADMIN_USER}" != "" ] ; then
	echo "from django.contrib.auth.models import User; User.objects.create_superuser('${WEB_ADMIN_USER}', '${WEB_ADMIN_EMAIL}', '${WEB_ADMIN_PASS}')" | python manage.py shell
else
	python "${SAMPLE_DIR}"/../manage.py createsuperuser
fi

# Set a user profile for the django user added by the step above:
echo "insert into cavedb_caveuserprofile values (1, 1, true, true, true);" | psql "${DBNAME}"

# Create empty data directory
mkdir -p "${CAVEDB_DATA_BASE_DIR}"/gis_maps/

# Copy GIS legend for PDF
cp "${SAMPLE_DIR}"/legend.png "${CAVEDB_DATA_BASE_DIR}"/gis_maps/

# Symlink in mapserver files
ln -s "${POSTGIS_DATA_IMPORTER_BASE_DIR}"/download/us_wv/aerial/USDA-2014/2014.map "${CAVEDB_DATA_BASE_DIR}"/gis_maps/
ln -s "${POSTGIS_DATA_IMPORTER_BASE_DIR}"/download/us_wv/aerial/SAMB-2003/JPG/2003.map "${CAVEDB_DATA_BASE_DIR}"/gis_maps/
ln -s "${POSTGIS_DATA_IMPORTER_BASE_DIR}"/download/us_wv/hillshade/hillshade.map "${CAVEDB_DATA_BASE_DIR}"/gis_maps/
touch "${CAVEDB_DATA_BASE_DIR}"/gis_maps/topo.map

# Install the West Virginia base data. This is for the GIS layers, counties,
# topo quads, topo quad / county relationships, and UTM zones for the entire
# state.

psql "${DBNAME}" < "${SAMPLE_DIR}"/wv-base-data.sql

# Copy sample entrance photos and maps:
cp -dpRv "${SAMPLE_DIR}"/feature_attachments/ "${CAVEDB_DATA_BASE_DIR}"

# Add sample bulletin data to PostgreSQL:
psql "${DBNAME}" < "${SAMPLE_DIR}"/sample-bulletin.sql

