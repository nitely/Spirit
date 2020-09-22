.. _upgrade:

Upgrade
=======

.. Warning::
    Make a database backup before upgrading to avoid data loss,
    you have been warned. Use the ``pg_dump`` command on PostgreSQL or
    ``mysqldump`` on MySQL. You can also create a backup running python
    ``python manage.py dumpdata --indent=4 > database.json``.
    You may want to backup the media folder as well.

Upgrade a minor version
-----------------------

Trying to skip a minor version while upgrading will
break things. For example, it's not possible to upgrade
from ``v0.4.x`` to ``v0.6.x`` without upgrading to ``v0.5.x`` first.

Make sure to check the changelog for every patch version
of the upgrade target, and make changes accordingly;
ex: added/removed installed apps, new settings, etc.
Check the Django logs for Spirit deprecation warnings.

Run the install command. Replace ``x`` by the next minor version.
Replace ``y`` by the latest patch version::

    pip install --upgrade django-spirit==0.x.y

Run the upgrade command. This command will run
``migrate``, ``rebuild_index``, and ``collectstatic``::

    python manage.py spiritupgrade

Upgrade a patch version
-----------------------

Unlike minor versions, it's possible to skip patch versions,
ex: upgrade from ``v0.4.x`` to ``v0.4.xx``. This is because patch versions
should not introduce breaking changes. However, it's advised to
always backup the data base, media folder, and current setup if
at all possible. Upgrades are not risk free.

Upgrade from +v0.1 to v0.4
--------------------------

Read the `Wiki <https://github.com/nitely/Spirit/wiki/Upgrading>`_.
