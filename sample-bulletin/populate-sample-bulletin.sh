#!/bin/bash -e

SAMPLE_DIR=$(dirname "$0")

WHOAMI=$(whoami)

DBNAME=cavedb
DATA_DEST_DIR=/usr/local/cavedbmanager-data
POSTGIS_DATA_IMPORTER_BASE_DIR=/home/"${WHOAMI}"/data/code/postgis-data-importer

# Create an empty PostgreSQL database for the cave data
createdb "${DBNAME}"

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
sudo mkdir -p "${DATA_DEST_DIR}"/gis_maps/
sudo chown -R "${WHOAMI}":"${WHOAMI}" "${DATA_DEST_DIR}"

# Copy GIS legend for PDF
cp "${SAMPLE_DIR}"/legend.png "${DATA_DEST_DIR}"/gis_maps/

# Symlink in mapserver files
ln -s "${POSTGIS_DATA_IMPORTER_BASE_DIR}"/download/us_wv/aerial/USDA-2014/2014.map "${DATA_DEST_DIR}"/gis_maps/
ln -s "${POSTGIS_DATA_IMPORTER_BASE_DIR}"/download/us_wv/aerial/SAMB-2003/JPG/2003.map "${DATA_DEST_DIR}"/gis_maps/
ln -s "${POSTGIS_DATA_IMPORTER_BASE_DIR}"/download/us_wv/hillshade/hillshade.map "${DATA_DEST_DIR}"/gis_maps/
touch "${DATA_DEST_DIR}"/gis_maps/topo.map

# Install the West Virginia base data. This is for the GIS layers, counties,
# topo quads, topo quad / county relationships, and UTM zones for the entire
# state.

psql "${DBNAME}" < "${SAMPLE_DIR}"/wv-base-data.sql

# Copy sample entrance photos and maps:
cp -dpRv "${SAMPLE_DIR}"/feature_attachments/ "${DATA_DEST_DIR}"

# Add sample bulletin data to PostgreSQL:
psql "${DBNAME}" < "${SAMPLE_DIR}"/sample-bulletin.sql

