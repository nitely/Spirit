# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('spirit_comment', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommentFlag',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_closed', models.BooleanField(default=False)),
                ('comment', models.OneToOneField(to='spirit_comment.Comment', on_delete=models.CASCADE)),
                ('moderator', models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, blank=True, on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name_plural': 'comments flags',
                'ordering': ['-date', '-pk'],
                'verbose_name': 'comment flag',
            },
        ),
        migrations.CreateModel(
            name='Flag',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('reason', models.IntegerField(choices=[(0, 'Spam'), (1, 'Other')], verbose_name='reason')),
                ('body', models.TextField(verbose_name='body', blank=True)),
                ('comment', models.ForeignKey(to='spirit_comment.Comment', on_delete=models.CASCADE)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name_plural': 'flags',
                'ordering': ['-date', '-pk'],
                'verbose_name': 'flag',
            },
        ),
        migrations.AlterUniqueTogether(
            name='flag',
            unique_together=set([('user', 'comment')]),
        ),
    ]
