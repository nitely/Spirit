# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('spirit_category', '0003_auto_20150810_1911'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='restrict_access',
            field=models.ManyToManyField(related_name='categories_access', verbose_name='visible to', to='auth.Group', blank=True),
        ),
        migrations.AddField(
            model_name='category',
            name='restrict_comment',
            field=models.ManyToManyField(related_name='categories_comment', verbose_name='comments can be posted by', to='auth.Group', blank=True),
        ),
        migrations.AddField(
            model_name='category',
            name='restrict_topic',
            field=models.ManyToManyField(related_name='categories_topic', verbose_name='topics can be created by', to='auth.Group', blank=True),
        ),
    ]
