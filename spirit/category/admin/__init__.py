# -*- coding: utf-8 -*-

from __future__ import unicode_literals

default_app_config = 'spirit.category.admin.apps.SpiritCategoryAdminConfig'


from django.contrib import admin
from ..models import Category


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'parent', 'is_closed', 'is_removed', 'is_private')
    list_filter = ('parent',)


admin.site.register(Category, CategoryAdmin)
