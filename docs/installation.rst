.. _installation:

Installation
============

Compatibility
-------------

* Python 2.7, 3.4, 3.5 and 3.6 (recommended)
* Django 1.8 LTS, 1.9, 1.10 and 1.11 LTS (recommended)
* PostgreSQL (recommended), MySQL, Oracle Database and SQLite

Get started
-----------

Latest version can be installed through pip::

1. Install Spirit::

    pip install django-spirit

2. Start your site::

    spirit startproject mysite

3. Set up the database::

    cd mysite
    python manage.py spiritinstall

4. Create an administrator account::

    python manage.py createsuperuser
    python manage.py runserver

Now sign in at http://127.0.0.1:8000/

Side notes
----------

This will run using the `developer` settings.
Running a production site is out of the scope
of this documentation. However there are many
guides about running a Django site out there.

Here are some hints:

* On production, create a ``prod_local.py``,
  import the production settings ``from .prod import *``
  and override settings such as ``DATABASES`` and ``ALLOWED_HOSTS``.
* Gunicorn and Nginx are a common way of running Python sites.
* An email server is required. There are self-hosted ones (ie: `exim <http://www.exim.org/>`_),
  and managed ones (ie: `Postmark <https://postmarkapp.com/>`_).
* A search engine is required. `Woosh <https://bitbucket.org/mchaput/whoosh/wiki/Home>`_
  comes configured by default, however is quite slow. A better choice may be elastic-search.
