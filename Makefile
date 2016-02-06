
help:
	@echo
	@echo make run ......... Start testing webserver
	@echo make installdb ... Build database
	@echo make destroymydb . Nuke and rebuild database
	@echo make clean ....... Delete filesystem build artifacts
	@echo

run: installdb
	#./manage.py runserver 0.0.0.0:8000 --adminmedia=media
	./manage.py runserver 8000 --adminmedia=media

installdb:
	./manage.py syncdb

destroymydb:
	./manage.py sqlreset cavedb | ./manage.py dbshell

clean:
	find . -name "*.pyc" | xargs rm -f
