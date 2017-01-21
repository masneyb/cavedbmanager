help:
	@echo make run ......... Start webserver bound to localhost
	@echo make runRemote ... Start webserver bound to all network interfaces
	@echo make lint ........ Run pylint against the code
	@echo make test ........ Run unit tests
	@echo make clean ....... Delete filesystem build artifacts

run:
	./manage.py runserver 8000

runRemote:
	./manage.py runserver 0.0.0.0:8000

lint:
	pylint --load-plugins pylint_django --disable=missing-docstring,locally-disabled cavedb/*.py cavedb/scripts/*.py cavedb/tests/*.py

test:
	python -m unittest discover

clean:
	find . -name "*.pyc" -delete
