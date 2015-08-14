# Spirit

[![Build Status](https://img.shields.io/travis/nitely/Spirit.svg?style=flat-square)](https://travis-ci.org/nitely/Spirit)
[![Coverage Status](https://img.shields.io/coveralls/nitely/Spirit.svg?style=flat-square)](https://coveralls.io/r/nitely/Spirit)
[![pypi](https://img.shields.io/pypi/v/django-spirit.svg?style=flat-square)](https://pypi.python.org/pypi/django-spirit)
[![licence](https://img.shields.io/pypi/l/django-spirit.svg?style=flat-square)](https://raw.githubusercontent.com/nitely/Spirit/master/LICENSE)

Spirit is a Python based forum built using the Django framework.

To see it in action, please visit [The Spirit Project](http://spirit-project.com/).

## Requirements

* Python 2.7, 3.3 or 3.4 (recommended)
* Django 1.8 LTS
* PostgreSQL (recommended) or MySQL or Oracle Database

## Dependencies

Check out the [requirements](https://github.com/nitely/Spirit/blob/master/requirements.txt) provided.

## Installing (Advanced)

Check out the [example](https://github.com/nitely/Spirit/tree/master/example) provided.

In short:

Add `url(r'^', include('spirit.urls')),` to your *urls.py*

Add `from spirit.settings import *` to the top of your *settings.py* file,
otherwise you will have to setup all django's related constants (Installed_apps, Middlewares, Login_url, etc)

Run:

    pip install -r requirements.txt
    python manage.py spiritinstall

> You will need to setup a search engine,
> Spirit is configured to work with [Woosh](https://bitbucket.org/mchaput/whoosh/wiki/Home) by default.
>
> An email server is required, you can host your own (ie: [exim](http://www.exim.org/)),
> or hire an external service provider (ie: [Mandrill](http://mandrill.com/)).

Start a development server:

    python manage.py runserver

Visit (http://127.0.0.1:8000/)

> On production, you would rather run Spirit on a real web server. ie: gunicorn + Nginx.
> Running Spirit on a [virtualenv](http://www.virtualenv.org) is adviced.

## Upgrading

Detailed upgrade instructions are listed in [Upgrading Spirit](https://github.com/nitely/Spirit/wiki/Upgrading)

## Testing

The `runtests.py` script enable you to run the test suite of spirit.

- Type `./runtests.py` to run the test suite using the settings from the `spirit` folder.
- Type `./runtests.py example` to run the test suite using the settings from the `example` folder.

## License

MIT
