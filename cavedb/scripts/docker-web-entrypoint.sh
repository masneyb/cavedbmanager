#!/bin/bash -u
# SPDX-License-Identifier: Apache-2.0

# Give PostgreSQL some time to start up
sleep 5

# Check if the database exists.
DB=$(psql -lqt root | awk '{print $1}' | grep -w "${PGDATABASE}")
if [ "${DB}" == "" ] ; then
	createdb "${PGDATABASE}"

	BACKUP_FILE="${CAVEDB_DATA_BASE_DIR}"/cavedb.sql
	if [ -f "${BACKUP_FILE}" ] ; then
		echo "Importing existing backup file ${BACKUP_FILE}..."

		psql "${PGDATABASE}" < "${BACKUP_FILE}"

		echo "Finished importing backup file ${BACKUP_FILE}."
	else
		echo "Populating sample bulletin data..."

		./sample-bulletin/populate-sample-bulletin.sh
		chown -R www-data:www-data "${CAVEDB_DATA_BASE_DIR}"

		echo "Finished populating sample bulletin data."
	fi
fi

if [ ! -f "${SSL_COMBINED_CERTS}" ] || [ ! -f "${SSL_KEY}" ] ; then
	./cavedb/scripts/create-self-signed-https-certificate.sh
fi

supervisord -n -c /etc/supervisor/supervisord.conf
