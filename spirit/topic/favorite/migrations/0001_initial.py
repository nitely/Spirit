# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('spirit_topic', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TopicFavorite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('topic', models.ForeignKey(to='spirit_topic.Topic', on_delete=models.CASCADE)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ['-date', '-pk'],
                'verbose_name_plural': 'favorites',
                'verbose_name': 'favorite',
            },
        ),
        migrations.AlterUniqueTogether(
            name='topicfavorite',
            unique_together=set([('user', 'topic')]),
        ),
    ]
