# -*- coding: utf-8 -*-
from django.db import models, migrations
import django.utils.timezone
import django.contrib.auth.models
import spirit.core.utils.models
import re
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('slug', spirit.core.utils.models.AutoSlugField(populate_from='username', db_index=False, blank=True)),
                ('location', models.CharField(max_length=75, verbose_name='location', blank=True)),
                ('last_seen', models.DateTimeField(auto_now=True, verbose_name='last seen')),
                ('last_ip', models.GenericIPAddressField(null=True, verbose_name='last ip', blank=True)),
                ('timezone', models.CharField(default='UTC', choices=[('Etc/GMT+12', '(GMT -12:00) Eniwetok, Kwajalein'), ('Etc/GMT+11', '(GMT -11:00) Midway Island, Samoa'), ('Etc/GMT+10', '(GMT -10:00) Hawaii'), ('Pacific/Marquesas', '(GMT -9:30) Marquesas Islands'), ('Etc/GMT+9', '(GMT -9:00) Alaska'), ('Etc/GMT+8', '(GMT -8:00) Pacific Time (US & Canada)'), ('Etc/GMT+7', '(GMT -7:00) Mountain Time (US & Canada)'), ('Etc/GMT+6', '(GMT -6:00) Central Time (US & Canada), Mexico City'), ('Etc/GMT+5', '(GMT -5:00) Eastern Time (US & Canada), Bogota, Lima'), ('America/Caracas', '(GMT -4:30) Venezuela'), ('Etc/GMT+4', '(GMT -4:00) Atlantic Time (Canada), Caracas, La Paz'), ('Etc/GMT+3', '(GMT -3:00) Brazil, Buenos Aires, Georgetown'), ('Etc/GMT+2', '(GMT -2:00) Mid-Atlantic'), ('Etc/GMT+1', '(GMT -1:00) Azores, Cape Verde Islands'), ('UTC', '(GMT) Western Europe Time, London, Lisbon, Casablanca'), ('Etc/GMT-1', '(GMT +1:00) Brussels, Copenhagen, Madrid, Paris'), ('Etc/GMT-2', '(GMT +2:00) Kaliningrad, South Africa'), ('Etc/GMT-3', '(GMT +3:00) Baghdad, Riyadh, Moscow, St. Petersburg'), ('Etc/GMT-4', '(GMT +4:00) Abu Dhabi, Muscat, Baku, Tbilisi'), ('Asia/Kabul', '(GMT +4:30) Afghanistan'), ('Etc/GMT-5', '(GMT +5:00) Ekaterinburg, Islamabad, Karachi, Tashkent'), ('Asia/Kolkata', '(GMT +5:30) India, Sri Lanka'), ('Asia/Kathmandu', '(GMT +5:45) Nepal'), ('Etc/GMT-6', '(GMT +6:00) Almaty, Dhaka, Colombo'), ('Indian/Cocos', '(GMT +6:30) Cocos Islands, Myanmar'), ('Etc/GMT-7', '(GMT +7:00) Bangkok, Hanoi, Jakarta'), ('Etc/GMT-8', '(GMT +8:00) Beijing, Perth, Singapore, Hong Kong'), ('Australia/Eucla', '(GMT +8:45) Australia (Eucla)'), ('Etc/GMT-9', '(GMT +9:00) Tokyo, Seoul, Osaka, Sapporo, Yakutsk'), ('Australia/North', '(GMT +9:30) Australia (Northern Territory)'), ('Etc/GMT-10', '(GMT +10:00) Eastern Australia, Guam, Vladivostok'), ('Etc/GMT-11', '(GMT +11:00) Magadan, Solomon Islands, New Caledonia'), ('Pacific/Norfolk', '(GMT +11:30) Norfolk Island'), ('Etc/GMT-12', '(GMT +12:00) Auckland, Wellington, Fiji, Kamchatka')], max_length=32, verbose_name='time zone')),
                ('is_administrator', models.BooleanField(default=False, verbose_name='administrator status')),
                ('is_moderator', models.BooleanField(default=False, verbose_name='moderator status')),
                ('is_verified', models.BooleanField(default=False, help_text='Designates whether the user has verified his account by email or by other means. Un-select this to let the user activate his account.', verbose_name='verified')),
                ('topic_count', models.PositiveIntegerField(default=0, verbose_name='topic count')),
                ('comment_count', models.PositiveIntegerField(default=0, verbose_name='comment count')),
                ('username', models.CharField(unique=True, db_index=True, verbose_name='username', validators=[django.core.validators.RegexValidator(re.compile('^[\\w.@+-]+$', 32), 'Enter a valid username.', 'invalid')], help_text='Required. 30 characters or fewer. Letters, numbers and @/./+/-/_ characters', max_length=30)),
                ('first_name', models.CharField(max_length=30, verbose_name='first name', blank=True)),
                ('last_name', models.CharField(max_length=30, verbose_name='last name', blank=True)),
                ('email', models.EmailField(unique=True, max_length=254, verbose_name='email')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('groups', models.ManyToManyField(related_query_name='user', verbose_name='groups', blank=True, to='auth.Group', help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set')),
                ('user_permissions', models.ManyToManyField(related_query_name='user', verbose_name='user permissions', blank=True, to='auth.Permission', help_text='Specific permissions for this user.', related_name='user_set')),
            ],
            options={
                'verbose_name_plural': 'users',
                'ordering': ['-date_joined', '-pk'],
                'db_table': 'spirit_user_user',
                'verbose_name': 'user',
                'abstract': False,
                'swappable': 'AUTH_USER_MODEL',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('slug', spirit.core.utils.models.AutoSlugField(populate_from='user.username', db_index=False, blank=True)),
                ('location', models.CharField(max_length=75, verbose_name='location', blank=True)),
                ('last_seen', models.DateTimeField(auto_now=True, verbose_name='last seen')),
                ('last_ip', models.GenericIPAddressField(null=True, verbose_name='last ip', blank=True)),
                ('timezone', models.CharField(default='UTC', choices=[('Etc/GMT+12', '(GMT -12:00) Eniwetok, Kwajalein'), ('Etc/GMT+11', '(GMT -11:00) Midway Island, Samoa'), ('Etc/GMT+10', '(GMT -10:00) Hawaii'), ('Pacific/Marquesas', '(GMT -9:30) Marquesas Islands'), ('Etc/GMT+9', '(GMT -9:00) Alaska'), ('Etc/GMT+8', '(GMT -8:00) Pacific Time (US & Canada)'), ('Etc/GMT+7', '(GMT -7:00) Mountain Time (US & Canada)'), ('Etc/GMT+6', '(GMT -6:00) Central Time (US & Canada), Mexico City'), ('Etc/GMT+5', '(GMT -5:00) Eastern Time (US & Canada), Bogota, Lima'), ('America/Caracas', '(GMT -4:30) Venezuela'), ('Etc/GMT+4', '(GMT -4:00) Atlantic Time (Canada), Caracas, La Paz'), ('Etc/GMT+3', '(GMT -3:00) Brazil, Buenos Aires, Georgetown'), ('Etc/GMT+2', '(GMT -2:00) Mid-Atlantic'), ('Etc/GMT+1', '(GMT -1:00) Azores, Cape Verde Islands'), ('UTC', '(GMT) Western Europe Time, London, Lisbon, Casablanca'), ('Etc/GMT-1', '(GMT +1:00) Brussels, Copenhagen, Madrid, Paris'), ('Etc/GMT-2', '(GMT +2:00) Kaliningrad, South Africa'), ('Etc/GMT-3', '(GMT +3:00) Baghdad, Riyadh, Moscow, St. Petersburg'), ('Etc/GMT-4', '(GMT +4:00) Abu Dhabi, Muscat, Baku, Tbilisi'), ('Asia/Kabul', '(GMT +4:30) Afghanistan'), ('Etc/GMT-5', '(GMT +5:00) Ekaterinburg, Islamabad, Karachi, Tashkent'), ('Asia/Kolkata', '(GMT +5:30) India, Sri Lanka'), ('Asia/Kathmandu', '(GMT +5:45) Nepal'), ('Etc/GMT-6', '(GMT +6:00) Almaty, Dhaka, Colombo'), ('Indian/Cocos', '(GMT +6:30) Cocos Islands, Myanmar'), ('Etc/GMT-7', '(GMT +7:00) Bangkok, Hanoi, Jakarta'), ('Etc/GMT-8', '(GMT +8:00) Beijing, Perth, Singapore, Hong Kong'), ('Australia/Eucla', '(GMT +8:45) Australia (Eucla)'), ('Etc/GMT-9', '(GMT +9:00) Tokyo, Seoul, Osaka, Sapporo, Yakutsk'), ('Australia/North', '(GMT +9:30) Australia (Northern Territory)'), ('Etc/GMT-10', '(GMT +10:00) Eastern Australia, Guam, Vladivostok'), ('Etc/GMT-11', '(GMT +11:00) Magadan, Solomon Islands, New Caledonia'), ('Pacific/Norfolk', '(GMT +11:30) Norfolk Island'), ('Etc/GMT-12', '(GMT +12:00) Auckland, Wellington, Fiji, Kamchatka')], max_length=32, verbose_name='time zone')),
                ('is_administrator', models.BooleanField(default=False, verbose_name='administrator status')),
                ('is_moderator', models.BooleanField(default=False, verbose_name='moderator status')),
                ('is_verified', models.BooleanField(default=False, help_text='Designates whether the user has verified his account by email or by other means. Un-select this to let the user activate his account.', verbose_name='verified')),
                ('topic_count', models.PositiveIntegerField(default=0, verbose_name='topic count')),
                ('comment_count', models.PositiveIntegerField(default=0, verbose_name='comment count')),
                ('user', models.OneToOneField(verbose_name='profile', to=settings.AUTH_USER_MODEL, related_name='st', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name_plural': 'forum profiles',
                'verbose_name': 'forum profile',
            },
        ),
    ]
