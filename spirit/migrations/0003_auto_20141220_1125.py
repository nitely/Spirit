# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re

from django.db import models, migrations
import django.core.validators

import spirit.utils.models


class Migration(migrations.Migration):

    dependencies = [
        ('spirit', '0002_auto_20140928_2347'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='slug',
            field=spirit.utils.models.AutoSlugField(blank=True, populate_from='title', db_index=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='topic',
            name='slug',
            field=spirit.utils.models.AutoSlugField(blank=True, populate_from='title', db_index=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='topic',
            name='title',
            field=models.CharField(max_length=255, verbose_name='title'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='slug',
            field=spirit.utils.models.AutoSlugField(blank=True, populate_from='username', db_index=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='timezone',
            field=models.CharField(choices=[('Etc/GMT+12', '(GMT -12:00) Eniwetok, Kwajalein'), ('Etc/GMT+11', '(GMT -11:00) Midway Island, Samoa'), ('Etc/GMT+10', '(GMT -10:00) Hawaii'), ('Pacific/Marquesas', '(GMT -9:30) Marquesas Islands'), ('Etc/GMT+9', '(GMT -9:00) Alaska'), ('Etc/GMT+8', '(GMT -8:00) Pacific Time (US & Canada)'), ('Etc/GMT+7', '(GMT -7:00) Mountain Time (US & Canada)'), ('Etc/GMT+6', '(GMT -6:00) Central Time (US & Canada), Mexico City'), ('Etc/GMT+5', '(GMT -5:00) Eastern Time (US & Canada), Bogota, Lima'), ('America/Caracas', '(GMT -4:30) Venezuela'), ('Etc/GMT+4', '(GMT -4:00) Atlantic Time (Canada), Caracas, La Paz'), ('Etc/GMT+3', '(GMT -3:00) Brazil, Buenos Aires, Georgetown'), ('Etc/GMT+2', '(GMT -2:00) Mid-Atlantic'), ('Etc/GMT+1', '(GMT -1:00) Azores, Cape Verde Islands'), ('UTC', '(GMT) Western Europe Time, London, Lisbon, Casablanca'), ('Etc/GMT-1', '(GMT +1:00) Brussels, Copenhagen, Madrid, Paris'), ('Etc/GMT-2', '(GMT +2:00) Kaliningrad, South Africa'), ('Etc/GMT-3', '(GMT +3:00) Baghdad, Riyadh, Moscow, St. Petersburg'), ('Etc/GMT-4', '(GMT +4:00) Abu Dhabi, Muscat, Baku, Tbilisi'), ('Asia/Kabul', '(GMT +4:30) Afghanistan'), ('Etc/GMT-5', '(GMT +5:00) Ekaterinburg, Islamabad, Karachi, Tashkent'), ('Asia/Kolkata', '(GMT +5:30) India, Sri Lanka'), ('Asia/Kathmandu', '(GMT +5:45) Nepal'), ('Etc/GMT-6', '(GMT +6:00) Almaty, Dhaka, Colombo'), ('Indian/Cocos', '(GMT +6:30) Cocos Islands, Myanmar'), ('Etc/GMT-7', '(GMT +7:00) Bangkok, Hanoi, Jakarta'), ('Etc/GMT-8', '(GMT +8:00) Beijing, Perth, Singapore, Hong Kong'), ('Australia/Eucla', '(GMT +8:45) Australia (Eucla)'), ('Etc/GMT-9', '(GMT +9:00) Tokyo, Seoul, Osaka, Sapporo, Yakutsk'), ('Australia/North', '(GMT +9:30) Australia (Northern Territory)'), ('Etc/GMT-10', '(GMT +10:00) Eastern Australia, Guam, Vladivostok'), ('Etc/GMT-11', '(GMT +11:00) Magadan, Solomon Islands, New Caledonia'), ('Pacific/Norfolk', '(GMT +11:30) Norfolk Island'), ('Etc/GMT-12', '(GMT +12:00) Auckland, Wellington, Fiji, Kamchatka')], default='UTC', verbose_name='time zone', max_length=32),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=30, help_text='Required. 30 characters or fewer. Letters, numbers and @/./+/-/_ characters', verbose_name='username', validators=[django.core.validators.RegexValidator(re.compile('^[\\w.@+-]+$', 32), 'Enter a valid username.', 'invalid')], unique=True, db_index=True),
            preserve_default=True,
        ),
    ]
