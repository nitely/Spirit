# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spirit_topic', '0002_auto_20150828_2003'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='topic',
            options={'verbose_name': 'topic', 'ordering': ['-last_active', '-pk'], 'default_permissions': ('add', 'change', 'delete', 'read', 'add_comment_to'), 'verbose_name_plural': 'topics'},
        ),
    ]
