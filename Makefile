.PHONY: help run runRemote dockerRun diffsettings lint pylint shellcheck test ci clean

help:
	@echo make run ......... Start webserver bound to localhost
	@echo make runRemote ... Start webserver bound to all network interfaces
	@echo make diffsettings. Show all Django settings
	@echo make dockerRun ... Build and run Docker containers
	@echo make dockerStop .. Stop Docker containers
	@echo make lint ........ Run pylint against the code
	@echo make test ........ Run unit tests
	@echo make ci .......... Run CI tests
	@echo make clean ....... Delete filesystem build artifacts

run:
	./manage.py runserver 8000

runRemote:
	./manage.py runserver 0.0.0.0:8000

dockerBuildBase:
	docker build --file Dockerfile.base --tag cavedbmanager_base:latest .

dockerRun: dockerBuildBase
	mkdir -p docker-volumes/var-lib-postgresql docker-volumes/postgis-data-importer-downloads docker-volumes/cavedb-ssl docker-volumes/cavedb-worker docker-volumes/cavedbmanager-data
	docker-compose up --build

dockerStop:
	docker-compose down

diffsettings:
	./manage.py diffsettings --all

lint: pylint shellcheck


pylint:
	pylint cavedb/*.py cavedb/scripts/*.py cavedb/tests/*.py

shellcheck:
	shellcheck cavedb/scripts/backup-data.sh
	shellcheck cavedb/scripts/create-self-signed-https-certificate.sh
	shellcheck cavedb/scripts/docker-cron-entrypoint.sh
	shellcheck cavedb/scripts/docker-web-entrypoint.sh
	shellcheck cavedb/scripts/docker-worker-entrypoint.sh
	shellcheck cavedb/scripts/worker.sh
	shellcheck sample-bulletin/populate-sample-bulletin.sh

test:
	python3 -Wa manage.py test

ci: test lint


ctags:
	ctags -R cavedb/

clean:
	find . -name "*.pyc" -delete
