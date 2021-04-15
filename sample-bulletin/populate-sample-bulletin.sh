#!/bin/bash -eu
# SPDX-License-Identifier: Apache-2.0

SAMPLE_DIR=$(dirname "$0")

DBNAME=cavedb
POSTGIS_DATA_IMPORTER_BASE_DIR=/usr/local/postgis-data-importer

# Create the tables in the new database. It will prompt you to create a
# Django admin user that you will use to log into the website.
"${SAMPLE_DIR}"/../manage.py migrate
"${SAMPLE_DIR}"/../manage.py makemigrations cavedb
"${SAMPLE_DIR}"/../manage.py migrate cavedb

if [ "${WEB_ADMIN_USER}" != "" ] ; then
	echo "Creating user based on environment variables"
	echo "from django.contrib.auth.models import User; User.objects.create_superuser('${WEB_ADMIN_USER}', '${WEB_ADMIN_EMAIL}', '${WEB_ADMIN_PASS}')" | "${SAMPLE_DIR}"/../manage.py shell
else
	"${SAMPLE_DIR}"/../manage.py createsuperuser
fi

# Set a user profile for the django user added by the step above:
echo "insert into cavedb_caveuserprofile values (1, true, true, true, 1);" | psql "${DBNAME}"

# Create empty data directory
mkdir -p "${CAVEDB_DATA_BASE_DIR}"/gis_maps/

# Copy GIS legend for PDF
cp "${SAMPLE_DIR}"/legend.png "${CAVEDB_DATA_BASE_DIR}"/gis_maps/

# Symlink in mapserver files
if [ ! -f "${CAVEDB_DATA_BASE_DIR}"/gis_maps/topo.map ] ; then
	ln -s "${POSTGIS_DATA_IMPORTER_BASE_DIR}"/download/us_wv/aerial/USDA-2014/2014.map "${CAVEDB_DATA_BASE_DIR}"/gis_maps/
	ln -s "${POSTGIS_DATA_IMPORTER_BASE_DIR}"/download/us_wv/aerial/SAMB-2003/JPG/2003.map "${CAVEDB_DATA_BASE_DIR}"/gis_maps/
	ln -s "${POSTGIS_DATA_IMPORTER_BASE_DIR}"/download/us_wv/hillshade/hillshade.map "${CAVEDB_DATA_BASE_DIR}"/gis_maps/
	touch "${CAVEDB_DATA_BASE_DIR}"/gis_maps/topo.map
fi

# Install the West Virginia base data. This is for the GIS layers, counties,
# topo quads, topo quad / county relationships, and UTM zones for the entire
# state.

psql "${DBNAME}" < "${SAMPLE_DIR}"/wv-base-data.sql

# Copy sample entrance photos and maps:
cp -dpRv "${SAMPLE_DIR}"/feature_attachments/ "${CAVEDB_DATA_BASE_DIR}"

# Add sample bulletin data to PostgreSQL:
psql "${DBNAME}" < "${SAMPLE_DIR}"/sample-bulletin.sql

