# -*- coding: utf-8 -*-
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('spirit_category', '0004_category_color'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='reindex_at',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='modified at'),
        ),
    ]
