#!/bin/bash -v

# Give PostgreSQL some time to start up
sleep 5

# Check if the database exists.
psql -lqt root | awk '{print $1}' | grep -qw cavedb
if [ "$?" != "0" ] ; then
	cd ../postgis-data-importer

	mkdir download
	mkdir download/us_wv
	mkdir download/us_wv/hillshade
	mkdir download/us_wv/aerial
	mkdir download/us_wv/aerial/USDA-2014
	mkdir download/us_wv/aerial/SAMB-2003
	mkdir download/us_wv/aerial/SAMB-2003/MrSID
	mkdir download/us_wv/aerial/SAMB-2003/JPG
	mkdir download/us_wv/aerial/USGS-1994
	mkdir download/us_wv/dem
	mkdir download/us_wv/other

	patch -p1 < ../cavedbmanager/sample-bulletin/postgis-data-importer-sample-bulletin.patch

	make

	cd ../cavedbmanager

	./sample-bulletin/populate-sample-bulletin.sh
fi

make runRemote
