# -*- coding: utf-8 -*-
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('spirit_topic', '0002_auto_20150828_2003'),
    ]

    operations = [
        migrations.AddField(
            model_name='topic',
            name='reindex_at',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='reindex at'),
        ),
    ]
