# Spirit

[![Build Status](https://img.shields.io/github/actions/workflow/status/nitely/Spirit/ci.yml?branch=master&style=flat-square)](https://github.com/nitely/Spirit/actions?query=workflow%3ACI)
[![Coverage Status](https://img.shields.io/coveralls/nitely/Spirit/master.svg?style=flat-square)](https://coveralls.io/r/nitely/Spirit)
[![pypi](https://img.shields.io/pypi/v/django-spirit.svg?style=flat-square)](https://pypi.python.org/pypi/django-spirit)
[![licence](https://img.shields.io/pypi/l/django-spirit.svg?style=flat-square)](https://raw.githubusercontent.com/nitely/Spirit/master/LICENSE)

Spirit is a Python based forum built using the Django framework.

## Documentation

Docs can be found at [spirit.readthedocs.io](http://spirit.readthedocs.io/en/latest/)

## Compatibility

* Python 3.9, 3.10, 3.11, 3.12, 3.13
* Django 4.2 LTS, 5.2 LTS
* PostgreSQL (recommended), MySQL, Oracle Database and SQLite

Constrained by "[What Python version can I use with Django?](https://docs.djangoproject.com/en/dev/faq/install/#what-python-version-can-i-use-with-django)"

## Usage

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

## Dev

Use [uv tooling](https://docs.astral.sh/uv/).

### Testing

```
uv sync --all-extras
uv run spirit startproject test_project
uv run runtests.py
```

### Lint & Format

```
uvx ruff check --select I --fix
uvx ruff format
```

## License

MIT
