# -*- coding: utf-8 -*-
from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('spirit_user', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='comment_count',
        ),
        migrations.RemoveField(
            model_name='user',
            name='is_administrator',
        ),
        migrations.RemoveField(
            model_name='user',
            name='is_moderator',
        ),
        migrations.RemoveField(
            model_name='user',
            name='is_verified',
        ),
        migrations.RemoveField(
            model_name='user',
            name='last_ip',
        ),
        migrations.RemoveField(
            model_name='user',
            name='last_seen',
        ),
        migrations.RemoveField(
            model_name='user',
            name='location',
        ),
        migrations.RemoveField(
            model_name='user',
            name='slug',
        ),
        migrations.RemoveField(
            model_name='user',
            name='timezone',
        ),
        migrations.RemoveField(
            model_name='user',
            name='topic_count',
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(verbose_name='email address', blank=True, max_length=254),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.', 'invalid')], max_length=30, error_messages={'unique': 'A user with that username already exists.'}, verbose_name='username', help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', unique=True),
        ),
    ]
