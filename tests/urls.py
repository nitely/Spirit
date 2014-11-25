# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import patterns, include, url
from django.contrib import admin

# Override admin login for security purposes
from django.contrib.auth.decorators import login_required
admin.site.login = login_required(admin.site.login)


urlpatterns = patterns('',
                       url(r'^', include('spirit.urls', namespace="spirit", app_name="spirit")),
                       url(r'^admin/', include(admin.site.urls)),
                       )
