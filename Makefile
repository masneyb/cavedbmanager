help:
	@echo make run ......... Start webserver bound to localhost
	@echo make runRemote ... Start webserver bound to all network interfaces
	@echo make pylint ...... Run pylint against the code
	@echo make clean ....... Delete filesystem build artifacts

run:
	./manage.py runserver 8000

runRemote:
	./manage.py runserver 0.0.0.0:8000

pylint:
	pylint --load-plugins pylint_django --disable=missing-docstring,locally-disabled cavedb/*.py

test:
	python -m unittest discover

clean:
	find . -name "*.pyc" | xargs rm -f
