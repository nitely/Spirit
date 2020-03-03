# Spirit

[![Build Status](https://img.shields.io/travis/nitely/Spirit/master.svg?style=flat-square)](https://travis-ci.org/nitely/Spirit)
[![Coverage Status](https://img.shields.io/coveralls/nitely/Spirit/master.svg?style=flat-square)](https://coveralls.io/r/nitely/Spirit)
[![pypi](https://img.shields.io/pypi/v/django-spirit.svg?style=flat-square)](https://pypi.python.org/pypi/django-spirit)
[![licence](https://img.shields.io/pypi/l/django-spirit.svg?style=flat-square)](https://raw.githubusercontent.com/nitely/Spirit/master/LICENSE)

Spirit is a Python based forum built using the Django framework.

To see it in action, please visit [The Spirit Project](http://spirit-project.com/).

## Compatibility

* Python 3.5, 3.6, 3.7, and 3.8 (recommended)
* Django 2.2 LTS (recommended), and 3.0
* PostgreSQL (recommended), MySQL, Oracle Database and SQLite

Constrained by "[What Python version can I use with Django?](https://docs.djangoproject.com/en/2.1/faq/install/#what-python-version-can-i-use-with-django)"

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

For detailed installation and setup docs, see [spirit.readthedocs.io](http://spirit.readthedocs.io/en/latest/)

## Documentation

Docs can be found at [spirit.readthedocs.io](http://spirit.readthedocs.io/en/latest/)

## Testing

```
python runtests.py
```

## License

MIT
