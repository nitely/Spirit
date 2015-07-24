# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('spirit_topic', '0002_auto_20150724_2106'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('spirit', '0026_auto_20150724_2256')
    ]

    state_operations = [
        migrations.CreateModel(
            name='TopicPrivate',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('topic', models.ForeignKey(to='spirit_topic.Topic', related_name='topics_private')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'private topic',
                'verbose_name_plural': 'private topics',
                'db_table': 'spirit_private_topicprivate',
                'ordering': ['-date', '-pk'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='topicprivate',
            unique_together=set([('user', 'topic')]),
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=state_operations)
    ]
