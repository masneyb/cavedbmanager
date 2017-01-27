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

FIFO_DIR=$(dirname "${CAVEDB_WORKER_FIFO}")

if [ -e "${CAVEDB_WORKER_FIFO}" ] ; then
	rm "${CAVEDB_WORKER_FIFO}"
elif [ ! -d "${FIFO_DIR}" ] ; then
	mkdir -p "${FIFO_DIR}"
	chmod 0700 "${FIFO_DIR}"
fi

mkfifo -m 0600 "${CAVEDB_WORKER_FIFO}"
if [ $? != 0 ] ; then
	exit 1
fi

while true ; do
	BULLETIN_ID=$(cat "${CAVEDB_WORKER_FIFO}")
	if [[ ! "${BULLETIN_ID}" =~ ^[0-9]+$ ]] && [ "${BULLETIN_ID}" != "global" ]; then
		echo "Ignoring input ${BULLETIN_ID}"
		continue
	fi

	echo "Generating bulletin documents for bulletin_id ${BULLETIN_ID}"
	python /usr/local/cavedbmanager/cavedb/scripts/generate_single_bulletin.py "${BULLETIN_ID}"
done
