# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('spirit_topic', '0002_auto_20150724_2106'),
        ('spirit', '0018_auto_20150724_2153')
    ]

    state_operations = [
        migrations.CreateModel(
            name='TopicFavorite',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('topic', models.ForeignKey(to='spirit_topic.Topic')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'favorites',
                'verbose_name': 'favorite',
                'ordering': ['-date', '-pk'],
                'db_table': 'spirit_favorite_topicfavorite',
            },
        ),
        migrations.AlterUniqueTogether(
            name='topicfavorite',
            unique_together=set([('user', 'topic')]),
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=state_operations)
    ]
