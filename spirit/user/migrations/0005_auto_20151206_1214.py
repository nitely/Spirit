# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('spirit_user', '0004_auto_20150731_2351'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='given_likes_count',
            field=models.PositiveIntegerField(default=0, verbose_name='given likes count'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='received_likes_count',
            field=models.PositiveIntegerField(default=0, verbose_name='received likes count'),
        ),
    ]
