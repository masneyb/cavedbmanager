#!/bin/bash -v

# Give PostgreSQL some time to start up
sleep 5

# Check if the database exists.
psql -lqt root | awk '{print $1}' | grep -qw "${PGDATABASE}"
if [ "$?" != "0" ] ; then
	./sample-bulletin/populate-sample-bulletin.sh
fi

make runRemote
