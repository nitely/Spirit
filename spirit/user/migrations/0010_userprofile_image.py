# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-05-15 01:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spirit_user', '0009_auto_20161114_1850'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='image',
            field=models.ImageField(default='image/default.png', upload_to='image'),
        ),
    ]