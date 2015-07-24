# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('spirit_topic', '0002_auto_20150724_2106'),
        ('spirit_comment', '0002_auto_20150724_2212'),
        ('spirit', '0022_auto_20150724_2232')
    ]

    state_operations = [
        migrations.CreateModel(
            name='TopicNotification',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('action', models.IntegerField(default=0, choices=[(0, 'Undefined'), (1, 'Mention'), (2, 'Comment')])),
                ('is_read', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('comment', models.ForeignKey(null=True, to='spirit_comment.Comment', blank=True)),
                ('topic', models.ForeignKey(to='spirit_topic.Topic')),
                ('user', models.ForeignKey(verbose_name='user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'topic notification',
                'db_table': 'spirit_notification_topicnotification',
                'ordering': ['-date', '-pk'],
                'verbose_name_plural': 'topics notification',
            },
        ),
        migrations.AlterUniqueTogether(
            name='topicnotification',
            unique_together=set([('user', 'topic')]),
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=state_operations)
    ]
