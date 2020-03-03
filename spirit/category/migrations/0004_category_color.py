# -*- coding: utf-8 -*-
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spirit_category', '0003_category_is_global'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='color',
            field=models.CharField(max_length=7, verbose_name='color', blank=True,
                                   help_text="Title color in hex format (i.e: #1aafd0)."),
        ),
    ]
