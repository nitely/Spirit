# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('spirit_comment', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommentHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('comment_html', models.TextField(verbose_name='comment html')),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('comment_fk', models.ForeignKey(verbose_name='original comment', to='spirit_comment.Comment', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'comment history',
                'ordering': ['-date', '-pk'],
                'verbose_name_plural': 'comments history',
            },
        ),
    ]
