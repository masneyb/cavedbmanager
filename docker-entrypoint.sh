#!/bin/bash -v

# Give PostgreSQL some time to start up
sleep 5

# Check if the database exists.
psql -lqt root | awk '{print $1}' | grep -qw cavedb
if [ "$?" != "0" ] ; then
	cd ../postgis-data-importer
	patch -p1 < ../cavedbmanager/sample-bulletin/postgis-data-importer-sample-bulletin.patch

	make

	cd ../cavedbmanager

	./sample-bulletin/populate-sample-bulletin.sh
fi

make runRemote
