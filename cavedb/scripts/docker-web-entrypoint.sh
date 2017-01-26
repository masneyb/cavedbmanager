#!/bin/bash

# Give PostgreSQL some time to start up
sleep 5

# Check if the database exists.
psql -lqt root | awk '{print $1}' | grep -qw "${PGDATABASE}"
if [ "$?" != "0" ] ; then
	echo "Populating sample bulletin data..."

	./sample-bulletin/populate-sample-bulletin.sh

	echo "Finised populating sample bulletin data."
fi

make diffsettings runRemote
