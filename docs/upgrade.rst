.. _upgrade:

Upgrade
=======

.. Note::
    Upgrade steps for older versions can be found at the
    `Wiki <https://github.com/nitely/Spirit/wiki/Upgrading>`_

.. Warning::
    Make a database backup before upgrading to avoid data loss,
    you have been warned. Use the ``pg_dump`` command on PostgreSQL or
    ``mysqldump`` on MySQL. You can also create a backup running python
    ``python manage.py dumpdata --indent=4 > database.json``.
    You may want to backup the media folder as well.

.. Note::
    Make sure to check the changelog for every
    patch version of the upgrading target and
    make changes accordingly

.. Warning::
    Trying to skip a minor version while upgrading will break things. For example, it's
    not possible to upgrade from 0.4.x to 0.6.x without upgrading to 0.5.x first,
    however it's possible to skip patch versions, i.e: upgrade from 0.4.x to 0.4.xx

From v0.4.x to v0.5.x
---------------------

Starting from spirit v0.5, cloning the repo is no longer encouraged. Pip it instead.

Installation::

    pip install -I django-spirit==0.5.x
    # Replace the x by the latest patch version

Migration::

    python manage.py spiritupgrade
    # this will run ``migrate``, ``rebuild_index`` and ``collectstatic``

