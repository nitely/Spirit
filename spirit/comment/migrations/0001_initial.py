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
            name='Comment',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('comment', models.TextField(verbose_name='comment', max_length=3000)),
                ('comment_html', models.TextField(verbose_name='comment html')),
                ('action', models.IntegerField(default=0, verbose_name='action', choices=[(0, 'comment'), (1, 'topic moved'), (2, 'topic closed'), (3, 'topic unclosed'), (4, 'topic pinned'), (5, 'topic unpinned')])),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_removed', models.BooleanField(default=False)),
                ('is_modified', models.BooleanField(default=False)),
                ('ip_address', models.GenericIPAddressField(null=True, blank=True)),
                ('modified_count', models.PositiveIntegerField(default=0, verbose_name='modified count')),
                ('likes_count', models.PositiveIntegerField(default=0, verbose_name='likes count')),
                ('topic', models.ForeignKey(to='spirit_topic.Topic', on_delete=models.CASCADE)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='user', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name_plural': 'comments',
                'verbose_name': 'comment',
                'ordering': ['-date', '-pk'],
            },
        ),
    ]
