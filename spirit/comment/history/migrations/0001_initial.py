# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('spirit_comment', '0002_auto_20150724_2212'),
        ('spirit', '0034_auto_20150724_2321')
    ]

    state_operations = [
        migrations.CreateModel(
            name='CommentHistory',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('comment_html', models.TextField(verbose_name='comment html')),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('comment_fk', models.ForeignKey(to='spirit_comment.Comment', verbose_name='original comment')),
            ],
            options={
                'db_table': 'spirit_history_commenthistory',
                'ordering': ['-date', '-pk'],
                'verbose_name': 'comment history',
                'verbose_name_plural': 'comments history',
            },
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=state_operations)
    ]
