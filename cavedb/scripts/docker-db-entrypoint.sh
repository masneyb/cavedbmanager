#!/bin/sh -e

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

POSTGRES_BIN=/usr/lib/postgresql/9.5/bin/postgres
POSTGRES_UID=postgres
POSTGRES_GID=postgres

chown -R "${POSTGRES_UID}":"${POSTGRES_GID}" "${PGDATA}"

if [ -z "$(ls -A "${PGDATA}")" ]; then
	gosu "${POSTGRES_UID}" /usr/lib/postgresql/9.5/bin/initdb

	echo "listen_addresses='*'" >> "${PGDATA}"/postgresql.conf
	echo "host all all 0.0.0.0/0 md5" >> "${PGDATA}"/pg_hba.conf

	SQL="CREATE USER ${PGUSER} WITH SUPERUSER PASSWORD '${PGPASSWORD}';"
	echo "${SQL}" | gosu "${POSTGRES_UID}" "${POSTGRES_BIN}" --single -E

	SQL="CREATE DATABASE ${PGUSER};"
	echo "${SQL}" | gosu "${POSTGRES_UID}" "${POSTGRES_BIN}" --single -E
fi

exec gosu "${POSTGRES_UID}" "${POSTGRES_BIN}" -D "${PGDATA}"
