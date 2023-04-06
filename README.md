# Spirit

[![Build Status](https://img.shields.io/github/actions/workflow/status/nitely/Spirit/ci.yml?branch=master&style=flat-square)](https://github.com/nitely/Spirit/actions?query=workflow%3ACI)
[![Coverage Status](https://img.shields.io/coveralls/nitely/Spirit/master.svg?style=flat-square)](https://coveralls.io/r/nitely/Spirit)
[![pypi](https://img.shields.io/pypi/v/django-spirit.svg?style=flat-square)](https://pypi.python.org/pypi/django-spirit)
[![licence](https://img.shields.io/pypi/l/django-spirit.svg?style=flat-square)](https://raw.githubusercontent.com/nitely/Spirit/master/LICENSE)

Spirit is a Python based forum built using the Django framework.

To see it in action, please visit [The Spirit Project](http://spirit-project.com/).

## Documentation

Docs can be found at [spirit.readthedocs.io](http://spirit.readthedocs.io/en/latest/)

## Compatibility

* Python 3.8, 3.9, 3.10, and 3.11 (recommended)
* Django 3.2 LTS, and 4.2 LTS
* PostgreSQL (recommended), MySQL, Oracle Database and SQLite

Constrained by "[What Python version can I use with Django?](https://docs.djangoproject.com/en/dev/faq/install/#what-python-version-can-i-use-with-django)"

## Usage

> New in Spirit 0.5

```
pip install django-spirit
spirit startproject mysite
cd mysite
python manage.py spiritinstall
python manage.py createsuperuser
python manage.py runserver
```

Visit [http://127.0.0.1:8000](http://127.0.0.1:8000)

For detailed setup docs, see [spirit.readthedocs.io](http://spirit.readthedocs.io/en/latest/)

## Testing

```
python runtests.py
```

## License

MIT

## Sponsors

[<img src="https://opensource.nyc3.cdn.digitaloceanspaces.com/attribution/assets/PoweredByDO/DO_Powered_by_Badge_blue.svg" width="201" alt="Digital Ocean">](https://m.do.co/c/b8b19b89a73b)
