# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('spirit_category', '0002_auto_20150728_0442'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['order', 'title', 'pk'], 'verbose_name': 'category', 'verbose_name_plural': 'categories'},
        ),
        migrations.AddField(
            model_name='category',
            name='order',
            field=models.IntegerField(default=10, help_text='The order of the category in the list (lower number comes first)', verbose_name='order'),
        ),
    ]
