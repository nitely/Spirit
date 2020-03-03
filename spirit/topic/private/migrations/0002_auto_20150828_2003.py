# -*- coding: utf-8 -*-
from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('spirit_topic_private', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topicprivate',
            name='user',
            field=models.ForeignKey(related_name='st_topics_private', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
        ),
    ]
