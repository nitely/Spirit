# Spirit

[![Build Status](https://img.shields.io/travis/nitely/Spirit.svg?style=flat-square)](https://travis-ci.org/nitely/Spirit)
[![Coverage Status](https://img.shields.io/coveralls/nitely/Spirit.svg?style=flat-square)](https://coveralls.io/r/nitely/Spirit)
[![pypi](https://img.shields.io/pypi/v/django-spirit.svg?style=flat-square)](https://pypi.python.org/pypi/django-spirit)
[![licence](https://img.shields.io/pypi/l/django-spirit.svg?style=flat-square)](https://raw.githubusercontent.com/nitely/Spirit/master/LICENSE)

Spirit is a Python based forum built using the Django framework.

To see it in action, please visit [The Spirit Project](http://spirit-project.com/).

## Compatibility

* Python 2.7, 3.3, 3.4 (recommended) and 3.5
* Django 1.8 LTS
* PostgreSQL (recommended), MySQL, Oracle Database and SQLite

## Installing (Advanced)

Check out the [example project](https://github.com/nitely/Spirit/tree/master/example).

## Upgrading

Detailed upgrade instructions are listed in [Upgrading Spirit](https://github.com/nitely/Spirit/wiki/Upgrading)

## Testing

The `runtests.py` script enable you to run the test suite of spirit.

- Type `./runtests.py` to run the test suite using the settings from the `spirit` folder.
- Type `./runtests.py example` to run the test suite using the settings from the `example` folder.

## Docker Setup

1. Install [Docker Engine](https://docs.docker.com/engine/installation/).
2. Install [Docker Compose](https://docs.docker.com/compose/install/).
3. In Spirit's root directory, run `docker-compose up -d`.
4. Run `docker exec -ti REPLACE_WITH_SPIRIT_CONTAINER_NAME python manage.py createsuperuser` to create your super user.
5. On Linux, you may access Spirit at `127.0.0.1:8000`. If you are on OSX, I highly recommend using Kitematic, it helps with port forwarding.
6. Run `docker-compose run --rm spirit python runtests.py` to execute the tests.

## License

MIT
