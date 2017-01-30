#!/bin/bash -u

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
psql -lqt root | awk '{print $1}' | grep -qw "${PGDATABASE}"
if [ "$?" != "0" ] ; then
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

		echo "Finised populating sample bulletin data."
	fi
fi

if [ ! -f "${SSL_COMBINED_CERTS}" ] || [ ! -f "${SSL_KEY}" ] ; then
	./cavedb/scripts/create-self-signed-https-certificate.sh
fi

supervisord -n -c /etc/supervisor/supervisord.conf
