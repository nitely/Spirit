# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


def verify_active_users(apps, schema_editor):
    User = apps.get_model(settings.AUTH_USER_MODEL)

    if hasattr(User, 'is_verified'):
        User.objects.filter(is_active=True).update(is_verified=True)


class Migration(migrations.Migration):

    dependencies = [
        ('spirit', '0005_auto_20150327_0138'),
    ]

    operations = [
        migrations.RunPython(verify_active_users),
    ]
