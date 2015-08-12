# -*- coding: utf-8 -*-

from __future__ import unicode_literals

default_app_config = 'spirit.user.admin.apps.SpiritUserAdminConfig'


from django.contrib import admin
from ..models import UserProfile


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'last_seen', 'is_verified', 'is_administrator', 'is_moderator')


admin.site.register(UserProfile, UserProfileAdmin)