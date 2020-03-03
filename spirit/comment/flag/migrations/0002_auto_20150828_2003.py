# -*- coding: utf-8 -*-
from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('spirit_comment_flag', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commentflag',
            name='moderator',
            field=models.ForeignKey(related_name='st_comment_flags', blank=True, null=True, to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
        ),
        migrations.AlterField(
            model_name='flag',
            name='user',
            field=models.ForeignKey(related_name='st_flags', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
        ),
    ]
