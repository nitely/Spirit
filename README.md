# Spirit

[![Build Status](https://img.shields.io/travis/nitely/Spirit.svg?style=flat-square)](https://travis-ci.org/nitely/Spirit)
[![Coverage Status](https://img.shields.io/coveralls/nitely/Spirit.svg?style=flat-square)](https://coveralls.io/r/nitely/Spirit)
[![pypi](https://img.shields.io/pypi/v/django-spirit.svg?style=flat-square)](https://pypi.python.org/pypi/django-spirit)
[![licence](https://img.shields.io/pypi/l/django-spirit.svg?style=flat-square)](https://raw.githubusercontent.com/nitely/Spirit/master/LICENSE)

Spirit is a Python based forum built using the Django framework.

To see it in action, please visit [The Spirit Project](http://spirit-project.com/).

## Compatibility

* Python 2.7, 3.4 and 3.5 (recommended)
* Django 1.8 LTS (recommended), 1.9 and 1.10
* PostgreSQL (recommended), MySQL, Oracle Database and SQLite

## Usage

```python
pip install django-spirit
spirit startproject mysite
cd mysite
python manage.py spiritinstall
python manage.py createsuperuser
python manage.py runserver
```

Visit [http://127.0.0.1:8000](http://127.0.0.1:8000)

## Upgrading

Detailed upgrade instructions are listed in [Upgrading Spirit](https://github.com/nitely/Spirit/wiki/Upgrading)

## Testing

```python
$ python runtests.py
```

## License

MIT
