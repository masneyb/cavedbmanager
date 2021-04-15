#!/bin/bash -u
# SPDX-License-Identifier: Apache-2.0

POSTGRES_BIN=/usr/lib/postgresql/10/bin/postgres
POSTGRES_UID=postgres
POSTGRES_GID=postgres

chown -R "${POSTGRES_UID}":"${POSTGRES_GID}" "${PGDATA}"

if [ -z "$(ls -A "${PGDATA}")" ]; then
	gosu "${POSTGRES_UID}" /usr/lib/postgresql/10/bin/initdb

	echo "listen_addresses='*'" >> "${PGDATA}"/postgresql.conf
	echo "host all all 0.0.0.0/0 md5" >> "${PGDATA}"/pg_hba.conf

	SQL="CREATE USER ${PGUSER} WITH SUPERUSER PASSWORD '${PGPASSWORD}';"
	echo "${SQL}" | gosu "${POSTGRES_UID}" "${POSTGRES_BIN}" --single -E

	SQL="CREATE DATABASE ${PGUSER};"
	echo "${SQL}" | gosu "${POSTGRES_UID}" "${POSTGRES_BIN}" --single -E
fi

chmod 0700 "${PGDATA}"
exec gosu "${POSTGRES_UID}" "${POSTGRES_BIN}" -D "${PGDATA}"
