# -*- coding: utf-8 -*-
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
            name='TopicUnread',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_read', models.BooleanField(default=True)),
                ('topic', models.ForeignKey(to='spirit_topic.Topic', on_delete=models.CASCADE)),
                ('user', models.ForeignKey(verbose_name='user', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'topic unread',
                'ordering': ['-date', '-pk'],
                'verbose_name_plural': 'topics unread',
            },
        ),
        migrations.AlterUniqueTogether(
            name='topicunread',
            unique_together=set([('user', 'topic')]),
        ),
    ]
