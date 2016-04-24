# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spirit_category', '0003_category_is_global'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='colour',
            field=models.CharField(max_length=7, verbose_name='colour', blank=True),
        ),
    ]
