# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('spirit_topic', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TopicPrivate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('topic', models.ForeignKey(related_name='topics_private', to='spirit_topic.Topic', on_delete=models.CASCADE)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'private topic',
                'ordering': ['-date', '-pk'],
                'verbose_name_plural': 'private topics',
            },
        ),
        migrations.AlterUniqueTogether(
            name='topicprivate',
            unique_together=set([('user', 'topic')]),
        ),
    ]
