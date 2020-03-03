# -*- coding: utf-8 -*-
from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('spirit_topic_notification', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topicnotification',
            name='user',
            field=models.ForeignKey(related_name='st_topic_notifications', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
        ),
    ]
