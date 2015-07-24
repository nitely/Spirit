# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('spirit_comment', '0002_auto_20150724_2212'),
        ('spirit', '0032_auto_20150724_2315')
    ]

    state_operations = [
        migrations.CreateModel(
            name='CommentFlag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_closed', models.BooleanField(default=False)),
                ('comment', models.OneToOneField(to='spirit_comment.Comment')),
                ('moderator', models.ForeignKey(to=settings.AUTH_USER_MODEL, blank=True, null=True)),
            ],
            options={
                'db_table': 'spirit_flag_commentflag',
                'verbose_name': 'comment flag',
                'verbose_name_plural': 'comments flags',
                'ordering': ['-date', '-pk'],
            },
        ),
        migrations.CreateModel(
            name='Flag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('reason', models.IntegerField(verbose_name='reason', choices=[(0, 'Spam'), (1, 'Other')])),
                ('body', models.TextField(verbose_name='body', blank=True)),
                ('comment', models.ForeignKey(to='spirit_comment.Comment')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'spirit_flag_flag',
                'verbose_name': 'flag',
                'ordering': ['-date', '-pk'],
                'verbose_name_plural': 'flags',
            },
        ),
        migrations.AlterUniqueTogether(
            name='flag',
            unique_together=set([('user', 'comment')]),
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=state_operations)
    ]
