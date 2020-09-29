.. _task_manager:

Task Manager
============

Spirit ships with several tasks that run asynchronously.
The supported task managers to run these tasks are
`Huey <https://huey.readthedocs.io>`_, and
`Celery <https://docs.celeryproject.org>`_.

While Spirit can run without a task manager, some of the
tasks may not run, as they are too expensive to run as part
of the request-response cycle (web server), or they are require to be run
periodically.

Functionality that requires a task manager includes: search indexation.

Huey
----

Read the `Huey docs for Django <https://huey.readthedocs.io/en/latest/django.html>`_.

Install
*******

Run::

    pip install django-spirit[huey]

Configuration
*************

Set Huey as the Spirit task manager::

    # settings.py (dev.py or prod.py)

    # extend installed apps with +=
    INSTALLED_APPS += [
        'huey.contrib.djhuey',
    ]

    ST_TASK_MANAGER = 'huey'

The ``settings/prod.py`` and ``settings/dev.py`` files include sample
configuration for Huey. The ``prod.py`` settings set Redis as the backend,
and the ``dev.py`` settings set SQLite as the backend. Redis is recommended
for production environments, and it's a good option to use as the Django cache
as well.

How to install `Redis <https://redis.io/>`_ depends on the OS, for example
it can be installed as a Snap package in Ubuntu, or it can be run with docker.
So, it's out of the scope of these docs.

Run the tasks consumer
**********************

To start the task manager, run::

    python manage.py run_huey

This can be run with `supervisord <http://supervisord.org>`_,
or systemd in production.

The caveats of SQLite as a backend
**********************************

SQLite only works in single server instances, where
both the web-server and the task manager (Huey) are
running in the same machine, sharing the same SQLite
data base.

For sufficiently large forum instances, it's recommended
to run the task manager on its own machine, while the
web-server can scale up and down independently. This means
Redis must be used instead of SQLite.

Scaling Huey
************

I'm not aware of how well Huey scales horizontally. It seems
`it may just work fine <https://github.com/coleifer/huey/issues/195>`_.
However, all Huey instances but one must disable the periodic
task functionality to avoid running periodic tasks in more than
one machine. This can be done by passing the ``--no-periodic``
parameter to the task manager command.

Celery
------

Read the `Celery docs for Django <https://docs.celeryproject.org/en/latest/django/first-steps-with-django.html>`_.

Install
*******

Run::

    pip install django-spirit[celery]

Configuration
*************

Set Celery as the Spirit task manager::

    # mysite/settings/settings.py (dev.py or prod.py)

    ST_TASK_MANAGER = 'celery'

Import Celery at Django startup::

    # mysite/__init__.py

    from .celery import app as celery_app
    __all__ = ('celery_app',)

Run the tasks consumer
**********************

To start the task manager, run::

    celery -A mysite worker -l info

This can be run with `supervisord <http://supervisord.org>`_,
or systemd in production.

To start the periodic task manager, run::

    celery -A mysite beat -l info

Note this will just enqueue tasks that will later be consumed by the worker.

Celery does not work
********************

Celery likes to break all the things in every major version.
The celery configuration (including ``prod.py``, ``dev.py``, and
``mysite/celery.py``) were tested on ``v4.4.7``.

I'm not a Celery user. These docs and the Celery support are a
community effort. Please, send a PR if something breaks.
