.PHONY: help run runRemote dockerRun diffsettings lint test ci clean

help:
	@echo make run ......... Start webserver bound to localhost
	@echo make runRemote ... Start webserver bound to all network interfaces
	@echo make diffsettings. Show all Django settings
	@echo make dockerRun ... Build and run Docker containers
	@echo make lint ........ Run pylint against the code
	@echo make test ........ Run unit tests
	@echo make ci .......... Run CI tests
	@echo make clean ....... Delete filesystem build artifacts

run:
	./manage.py runserver 8000

runRemote:
	./manage.py runserver 0.0.0.0:8000

dockerRun:
	docker-compose up --build

diffsettings:
	./manage.py diffsettings --all

lint:
	pylint --load-plugins pylint_django \
		--disable=missing-docstring,locally-disabled cavedb/*.py \
		cavedb/scripts/*.py cavedb/tests/*.py
	shellcheck ./sample-bulletin/populate-sample-bulletin.sh
	shellcheck ./cavedb/scripts/docker-worker-entrypoint.sh
	shellcheck ./cavedb/scripts/docker-web-entrypoint.sh

test:
	python -m unittest discover

ci: test lint
	# NOOP

clean:
	find . -name "*.pyc" -delete
