# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import spirit.core.utils.models


class Migration(migrations.Migration):

    dependencies = [
        ('spirit', '0012_auto_20150724_1637'),
    ]

    state_operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('title', models.CharField(verbose_name='title', max_length=75)),
                ('slug', spirit.core.utils.models.AutoSlugField(db_index=False, populate_from='title', blank=True)),
                ('description', models.CharField(verbose_name='description', max_length=255, blank=True)),
                ('is_closed', models.BooleanField(verbose_name='closed', default=False)),
                ('is_removed', models.BooleanField(verbose_name='removed', default=False)),
                ('is_private', models.BooleanField(verbose_name='private', default=False)),
                ('parent', models.ForeignKey(verbose_name='category parent', blank=True, to='spirit_category.Category', null=True)),
            ],
            options={
                'verbose_name': 'category',
                'verbose_name_plural': 'categories',
                'db_table': 'spirit_category_category',
                'ordering': ['title', 'pk'],
            },
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=state_operations)
    ]