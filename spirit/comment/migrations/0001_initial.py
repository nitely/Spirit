# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('spirit_topic', '0002_auto_20150724_2106'),
        ('spirit', '0020_auto_20150724_2209')
    ]

    state_operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('comment', models.TextField(max_length=3000, verbose_name='comment')),
                ('comment_html', models.TextField(verbose_name='comment html')),
                ('action', models.IntegerField(default=0, choices=[(0, 'comment'), (1, 'topic moved'), (2, 'topic closed'), (3, 'topic unclosed'), (4, 'topic pinned'), (5, 'topic unpinned')], verbose_name='action')),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_removed', models.BooleanField(default=False)),
                ('is_modified', models.BooleanField(default=False)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('modified_count', models.PositiveIntegerField(default=0, verbose_name='modified count')),
                ('likes_count', models.PositiveIntegerField(default=0, verbose_name='likes count')),
                ('topic', models.ForeignKey(to='spirit_topic.Topic')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'db_table': 'spirit_comment_comment',
                'verbose_name_plural': 'comments',
                'ordering': ['-date', '-pk'],
                'verbose_name': 'comment',
            },
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=state_operations)
    ]
