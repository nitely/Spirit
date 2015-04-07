# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings

import spirit.utils.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('spirit', '0006_auto_20150327_0204'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('slug', spirit.utils.models.AutoSlugField(db_index=False, blank=True, populate_from='user.username')),
                ('location', models.CharField(blank=True, verbose_name='location', max_length=75)),
                ('last_seen', models.DateTimeField(auto_now=True, verbose_name='last seen')),
                ('last_ip', models.GenericIPAddressField(blank=True, verbose_name='last ip', null=True)),
                ('timezone', models.CharField(max_length=32, verbose_name='time zone', choices=[('Etc/GMT+12', '(GMT -12:00) Eniwetok, Kwajalein'), ('Etc/GMT+11', '(GMT -11:00) Midway Island, Samoa'), ('Etc/GMT+10', '(GMT -10:00) Hawaii'), ('Pacific/Marquesas', '(GMT -9:30) Marquesas Islands'), ('Etc/GMT+9', '(GMT -9:00) Alaska'), ('Etc/GMT+8', '(GMT -8:00) Pacific Time (US & Canada)'), ('Etc/GMT+7', '(GMT -7:00) Mountain Time (US & Canada)'), ('Etc/GMT+6', '(GMT -6:00) Central Time (US & Canada), Mexico City'), ('Etc/GMT+5', '(GMT -5:00) Eastern Time (US & Canada), Bogota, Lima'), ('America/Caracas', '(GMT -4:30) Venezuela'), ('Etc/GMT+4', '(GMT -4:00) Atlantic Time (Canada), Caracas, La Paz'), ('Etc/GMT+3', '(GMT -3:00) Brazil, Buenos Aires, Georgetown'), ('Etc/GMT+2', '(GMT -2:00) Mid-Atlantic'), ('Etc/GMT+1', '(GMT -1:00) Azores, Cape Verde Islands'), ('UTC', '(GMT) Western Europe Time, London, Lisbon, Casablanca'), ('Etc/GMT-1', '(GMT +1:00) Brussels, Copenhagen, Madrid, Paris'), ('Etc/GMT-2', '(GMT +2:00) Kaliningrad, South Africa'), ('Etc/GMT-3', '(GMT +3:00) Baghdad, Riyadh, Moscow, St. Petersburg'), ('Etc/GMT-4', '(GMT +4:00) Abu Dhabi, Muscat, Baku, Tbilisi'), ('Asia/Kabul', '(GMT +4:30) Afghanistan'), ('Etc/GMT-5', '(GMT +5:00) Ekaterinburg, Islamabad, Karachi, Tashkent'), ('Asia/Kolkata', '(GMT +5:30) India, Sri Lanka'), ('Asia/Kathmandu', '(GMT +5:45) Nepal'), ('Etc/GMT-6', '(GMT +6:00) Almaty, Dhaka, Colombo'), ('Indian/Cocos', '(GMT +6:30) Cocos Islands, Myanmar'), ('Etc/GMT-7', '(GMT +7:00) Bangkok, Hanoi, Jakarta'), ('Etc/GMT-8', '(GMT +8:00) Beijing, Perth, Singapore, Hong Kong'), ('Australia/Eucla', '(GMT +8:45) Australia (Eucla)'), ('Etc/GMT-9', '(GMT +9:00) Tokyo, Seoul, Osaka, Sapporo, Yakutsk'), ('Australia/North', '(GMT +9:30) Australia (Northern Territory)'), ('Etc/GMT-10', '(GMT +10:00) Eastern Australia, Guam, Vladivostok'), ('Etc/GMT-11', '(GMT +11:00) Magadan, Solomon Islands, New Caledonia'), ('Pacific/Norfolk', '(GMT +11:30) Norfolk Island'), ('Etc/GMT-12', '(GMT +12:00) Auckland, Wellington, Fiji, Kamchatka')], default='UTC')),
                ('is_administrator', models.BooleanField(verbose_name='administrator status', default=False)),
                ('is_moderator', models.BooleanField(verbose_name='moderator status', default=False)),
                ('is_verified', models.BooleanField(verbose_name='verified', help_text='Designates whether the user has verified his account by email or by other means. Un-select this to let the user activate his account.', default=False)),
                ('topic_count', models.PositiveIntegerField(verbose_name='topic count', default=0)),
                ('comment_count', models.PositiveIntegerField(verbose_name='comment count', default=0)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL, verbose_name='profile', related_name='st')),
            ],
            options={
                'verbose_name': 'forum profile',
                'verbose_name_plural': 'forum profiles',
            },
            bases=(models.Model,),
        ),
    ]
