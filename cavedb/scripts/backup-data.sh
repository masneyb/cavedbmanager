#!/bin/bash -eu
# SPDX-License-Identifier: Apache-2.0

if [ "${CAVEDB_DATA_BASE_DIR}" = "" ] ; then
	echo "usage: CAVEDB_DATA_BASE_DIR=<base directory> $0"
fi

cd "${CAVEDB_DATA_BASE_DIR}" || exit 1

if [ ! -d .git ] ; then
	git init
	echo "bulletins/" > .gitignore
fi

if [ ! -f .gitconfig ] ; then
	WHOAMI=$(whoami)
	git config --global user.email "${WHOAMI}@localhost"
	git config --global user.name "Backups"
fi

/usr/local/cavedbmanager/cavedb/scripts/generate_index_txt.py

pg_dump > "${CAVEDB_DATA_BASE_DIR}"/cavedb.sql

git add ./* .gitignore .gitconfig || true
git commit -m "Data backed up by $0" -a
