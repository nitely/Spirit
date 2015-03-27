# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models, migrations
import spirit.utils.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AutoSlugBadPopulateFromModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', spirit.utils.models.AutoSlugField(populate_from=b'bad')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AutoSlugDefaultModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', spirit.utils.models.AutoSlugField(default=b'foo')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AutoSlugModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', spirit.utils.models.AutoSlugField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AutoSlugPopulateFromModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, blank=True)),
                ('slug', spirit.utils.models.AutoSlugField(populate_from=b'title')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
