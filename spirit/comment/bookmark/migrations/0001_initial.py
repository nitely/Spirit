# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('spirit_topic', '0002_auto_20150724_2106'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('spirit', '0030_auto_20150724_2309')
    ]

    state_operations = [
        migrations.CreateModel(
            name='CommentBookmark',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('comment_number', models.PositiveIntegerField(default=0)),
                ('topic', models.ForeignKey(to='spirit_topic.Topic')),
                ('user', models.ForeignKey(verbose_name='user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'spirit_bookmark_commentbookmark',
                'verbose_name': 'comment bookmark',
                'verbose_name_plural': 'comments bookmarks',
            },
        ),
        migrations.AlterUniqueTogether(
            name='commentbookmark',
            unique_together=set([('user', 'topic')]),
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=state_operations)
    ]
