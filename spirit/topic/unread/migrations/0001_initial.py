# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('spirit_topic', '0002_auto_20150724_2106'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('spirit', '0028_auto_20150724_2304')
    ]

    state_operations = [
        migrations.CreateModel(
            name='TopicUnread',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_read', models.BooleanField(default=True)),
                ('topic', models.ForeignKey(to='spirit_topic.Topic')),
                ('user', models.ForeignKey(verbose_name='user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-date', '-pk'],
                'verbose_name': 'topic unread',
                'verbose_name_plural': 'topics unread',
                'db_table': 'spirit_unread_topicunread',
            },
        ),
        migrations.AlterUniqueTogether(
            name='topicunread',
            unique_together=set([('user', 'topic')]),
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=state_operations)
    ]
