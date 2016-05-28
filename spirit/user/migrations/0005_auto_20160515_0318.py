# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spirit_user', '0004_auto_20150731_2351'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='last_post_hash',
            field=models.CharField(blank=True, verbose_name='last post hash', max_length=32),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='last_post_on',
            field=models.DateTimeField(blank=True, verbose_name='last post on', null=True),
        ),
    ]
