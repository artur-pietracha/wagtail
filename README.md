# PY WAGTAIL API

Template for Python APIs using Django Rest Framework

[![circle-ci-image]][circle-ci]
[![codecov-image]][codecov]
[![black-image]][black]
[![gitflow-image]][gitflow]
[![calver-image]][calver]
[![cookiecutter-image]][cookiecutter]

## Rename app

In order to rename application firstly create remote repository on git provider such as github, or gitlab. Then run `rename.sh` script with following arguments;

    ./rename.sh APP_NAME_UNDERSCORE APP_NAME_DASH GIT_REMOTE_SSH_URL
EXAMPLE

    ./rename.sh app_name py-app-name git@github.com:user/py-app-name.git

## Setting up pre-commit hooks

    make hooks_setup

## Start app

    make run

Local (dev) env vars are set directly in `docker-compose.yml` file.

These env vars need to be set in prod:
```
    DJANGO_SETTINGS_MODULE=config.settings.production
    DJANGO_SECRET_KEY=
    DJANGO_ADMIN_URL=
    DJANGO_ALLOWED_HOSTS=
    DATABASE_URL=
    DATABASE_ATOMIC_REQUESTS=
    DATABASE_CONN_MAX_AGE=
    DJANGO_ALLOWED_HOSTS=
    PORT=
    HOST=

    DJANGO_SECURE_SSL_REDIRECT=False

    MAILGUN_API_KEY=
    MAILGUN_DOMAIN=
    DJANGO_SERVER_EMAIL=
    EMAIL_BACKEND=
    DJANGO_DEFAULT_FROM_EMAIL=

    # Gunicorn
    WEB_CONCURRENCY=4

    SENTRY_DSN=
```

## Create migrations

    make migrations

## Create superuser

To create an **superuser account**, use this command:

    make superuser

## Run tests

To run the tests and check your test coverage:

    make test 

[circle-ci-image]: https://circleci.com/gh/monterail/py-wagtail-api.svg?style=svg&circle-token=e43c768219e840ed326efa37a711ae7d522a276e
[circle-ci]: https://circleci.com/gh/monterail/py-wagtail-api/tree/master

[codecov-image]: https://codecov.io/gh/monterail/py-wagtail-api/branch/master/graph/badge.svg?token=LIYZPH7H8p
[codecov]: https://codecov.io/gh/monterail/py-wagtail-api

[black-image]: https://img.shields.io/badge/code%20style-black-000000.svg
[black]: https://github.com/psf/black

[gitflow-image]: https://img.shields.io/badge/Branching%20strategy-gitflow-5FBB1C.svg
[gitflow]: https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow

[calver-image]: https://img.shields.io/badge/Versioning%20strategy-CalVer-5FBB1C.svg
[calver]: https://calver.org

[cookiecutter-image]: https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg
[cookiecutter]: https://github.com/monterail/py-wagtail-api
