# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('spirit_category', '0004_category_color'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='modified_at',
            field=models.DateTimeField(verbose_name='modified at', default=django.utils.timezone.now),
        ),
    ]
