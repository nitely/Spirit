# -*- coding: utf-8 -*-

from __future__ import unicode_literals

default_app_config = 'spirit.topic.admin.apps.SpiritTopicAdminConfig'


from django.contrib import admin
from ..models import Topic


class TopicAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'category', 'date', 'user')
    list_filter = ('category',)
    raw_id_fields = ('user',)


admin.site.register(Topic, TopicAdmin)