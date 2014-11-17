# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import patterns, include, url


urlpatterns = patterns('',
                       url(r'^$', 'spirit.views.admin.index.dashboard', name='admin'),
                       url(r'^index/', include('spirit.urls.admin.index')),
                       url(r'^category/', include('spirit.urls.admin.category')),
                       url(r'^comment/flag/', include('spirit.urls.admin.comment_flag')),
                       url(r'^config/', include('spirit.urls.admin.config')),
                       url(r'^topic/', include('spirit.urls.admin.topic')),
                       url(r'^user/', include('spirit.urls.admin.user')),
                       )
