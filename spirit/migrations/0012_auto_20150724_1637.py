# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('spirit', '0011_auto_20150713_1032'),
    ]

    state_operations = [
        migrations.RemoveField(
            model_name='category',
            name='parent',
        ),
        migrations.AlterField(
            model_name='topic',
            name='category',
            field=models.ForeignKey(to='spirit_category.Category', verbose_name='category'),
        ),
        migrations.DeleteModel(
            name='Category',
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=state_operations)
    ]
