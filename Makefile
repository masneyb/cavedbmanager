
help:
	@echo
	@echo make run ......... Start testing webserver
	@echo make installdb ... Build database
	@echo make destroymydb . Nuke and rebuild database
	@echo make clean ....... Delete filesystem build artifacts
	@echo

# Only bind to the localhost interface
run: installdb
	./manage.py runserver 8000

# Bind to all network interfaces
runRemote: installdb
	./manage.py runserver 0.0.0.0:8000

installdb:
	./manage.py syncdb

destroymydb:
	./manage.py sqlreset cavedb | ./manage.py dbshell

clean:
	find . -name "*.pyc" | xargs rm -f
