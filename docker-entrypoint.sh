#!/bin/bash

# Check if the database exists
psql -lqt root | awk '{print $1}' | grep -qw cavedb
if [ "$?" != "0" ] ; then
	# Give PostgreSQL some time to start up
	sleep 5

	./sample-bulletin/populate-sample-bulletin.sh
fi

make runRemote
