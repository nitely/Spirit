# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('spirit_topic', '0001_initial'),
        ('spirit_comment', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='TopicNotification',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('action', models.IntegerField(default=0, choices=[(0, 'Undefined'), (1, 'Mention'), (2, 'Comment')])),
                ('is_read', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('comment', models.ForeignKey(to='spirit_comment.Comment')),
                ('topic', models.ForeignKey(to='spirit_topic.Topic')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'verbose_name_plural': 'topics notification',
                'verbose_name': 'topic notification',
                'ordering': ['-date', '-pk'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='topicnotification',
            unique_together=set([('user', 'topic')]),
        ),
    ]
