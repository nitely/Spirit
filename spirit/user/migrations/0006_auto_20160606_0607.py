# -*- coding: utf-8 -*-
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spirit_user', '0005_auto_20160515_0318'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='timezone',
            field=models.CharField(default='UTC', max_length=32, verbose_name='time zone'),
        ),
    ]
