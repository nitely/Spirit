# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import spirit.core.utils.models
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('spirit_category', '0002_auto_20150724_1644'),
        ('spirit', '0016_auto_20150724_2103')
    ]

    state_operations = [
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(verbose_name='title', max_length=255)),
                ('slug', spirit.core.utils.models.AutoSlugField(populate_from='title', db_index=False, blank=True)),
                ('date', models.DateTimeField(verbose_name='date', default=django.utils.timezone.now)),
                ('last_active', models.DateTimeField(verbose_name='last active', default=django.utils.timezone.now)),
                ('is_pinned', models.BooleanField(verbose_name='pinned', default=False)),
                ('is_globally_pinned', models.BooleanField(verbose_name='globally pinned', default=False)),
                ('is_closed', models.BooleanField(verbose_name='closed', default=False)),
                ('is_removed', models.BooleanField(default=False)),
                ('view_count', models.PositiveIntegerField(verbose_name='views count', default=0)),
                ('comment_count', models.PositiveIntegerField(verbose_name='comment count', default=0)),
                ('category', models.ForeignKey(verbose_name='category', to='spirit_category.Category')),
                ('user', models.ForeignKey(verbose_name='user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'topic',
                'db_table': 'spirit_topic_topic',
                'ordering': ['-last_active', '-pk'],
                'verbose_name_plural': 'topics',
            },
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=state_operations)
    ]
