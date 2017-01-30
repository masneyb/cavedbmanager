#!/bin/bash -eu

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

pg_dump > "${CAVEDB_DATA_BASE_DIR}"/cavedb.sql

git add ./* .gitignore .gitconfig
git commit -m "Data backed up by $0" -a
