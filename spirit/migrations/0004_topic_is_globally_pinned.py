# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('spirit', '0003_auto_20141220_1125'),
    ]

    operations = [
        migrations.AddField(
            model_name='topic',
            name='is_globally_pinned',
            field=models.BooleanField(default=False, verbose_name='globally pinned'),
            preserve_default=True,
        ),
    ]
