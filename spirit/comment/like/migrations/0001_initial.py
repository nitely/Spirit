# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('spirit_comment', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommentLike',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('comment', models.ForeignKey(related_name='comment_likes', to='spirit_comment.Comment', on_delete=models.CASCADE)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'like',
                'verbose_name_plural': 'likes',
                'ordering': ['-date', '-pk'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='commentlike',
            unique_together=set([('user', 'comment')]),
        ),
    ]
