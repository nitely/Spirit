# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('spirit_comment', '0002_auto_20150724_2212'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('spirit', '0037_auto_20150724_2329')
    ]

    state_operations = [
        migrations.CreateModel(
            name='CommentLike',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('comment', models.ForeignKey(to='spirit_comment.Comment', related_name='comment_likes')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'spirit_like_commentlike',
                'verbose_name_plural': 'likes',
                'ordering': ['-date', '-pk'],
                'verbose_name': 'like',
            },
        ),
        migrations.AlterUniqueTogether(
            name='commentlike',
            unique_together=set([('user', 'comment')]),
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=state_operations)
    ]
