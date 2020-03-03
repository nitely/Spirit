# -*- coding: utf-8 -*-
from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('spirit_topic', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CommentBookmark',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment_number', models.PositiveIntegerField(default=0)),
                ('topic', models.ForeignKey(to='spirit_topic.Topic', on_delete=models.CASCADE)),
                ('user', models.ForeignKey(verbose_name='user', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'comment bookmark',
                'verbose_name_plural': 'comments bookmarks',
            },
        ),
        migrations.AlterUniqueTogether(
            name='commentbookmark',
            unique_together=set([('user', 'topic')]),
        ),
    ]
