build: run

hooks_setup:
	pip install black flake8 isort[pyproject] pre-commit
	pre-commit install

# you can pass pytest args, e.g. `make test args='-k test_landing_page'` to run a single test
test:
	docker-compose run --rm appserver ./test.sh $(args)

test_failed:
	make test args='--last-failed'

test_ci:
	# this is so that codecov can get SHA
	echo '!'".git" >> .dockerignore
	docker-compose -f docker-compose.ci.yml run --rm sut ./test.sh

# allows using ipdb
run:
	docker-compose run --service-ports --rm appserver

shell:
	docker-compose run --rm appserver python manage.py shell

superuser:
	docker-compose run --rm appserver python manage.py createsuperuser

coverage_html:
	docker-compose run --rm appserver coverage html

migrations:
	docker-compose run --rm appserver python manage.py makemigrations

translations:
	docker-compose run --rm appserver python manage.py makemessages

reqs:
	pip-compile requirements/base.in
	pip-compile requirements/test.in
	pip-compile requirements/local.in
	pip-compile requirements/production.in
	docker-compose build

reqs_upgrade:
	pip-compile --upgrade requirements/base.in
	pip-compile --upgrade requirements/test.in
	pip-compile --upgrade requirements/local.in
	pip-compile --upgrade requirements/production.in
	docker-compose build

HEROKU_INSTALL_CLI := ./docker/install_heroku_cli.sh
HEROKU_LOGIN := docker login --username=$$HEROKU_EMAIL --password=$$HEROKU_TOKEN registry.heroku.com
HEROKU_CLI :=  ~/bin/heroku-cli/bin/heroku
HEROKU_PUSH_CONTAINER := $(HEROKU_CLI) container:push web worker scheduler --recursive --app
HEROKU_RELEASE_CONTAINER := $(HEROKU_CLI) container:release web worker scheduler --app
INSTALL_HEROKU_CLI_AND_LOGIN_AND_SETUP_DOCKERFILES := $(HEROKU_INSTALL_CLI) && $(HEROKU_LOGIN) && mv docker/production/django/Dockerfile.* ./

deploy_test:
	$(INSTALL_HEROKU_CLI_AND_LOGIN_AND_SETUP_DOCKERFILES)
	$(HEROKU_PUSH_CONTAINER) py-wagtail-api-test
	$(HEROKU_RELEASE_CONTAINER) py-wagtail-api-test

deploy_stage:
	$(INSTALL_HEROKU_CLI_AND_LOGIN_AND_SETUP_DOCKERFILES)
	$(HEROKU_PUSH_CONTAINER) py-wagtail-api-stage
	$(HEROKU_RELEASE_CONTAINER) py-wagtail-api-stage

deploy_prod:
	$(INSTALL_HEROKU_CLI_AND_LOGIN_AND_SETUP_DOCKERFILES)
	$(HEROKU_PUSH_CONTAINER) py-wagtail-api-prod
	$(HEROKU_RELEASE_CONTAINER) py-wagtail-api-prod
