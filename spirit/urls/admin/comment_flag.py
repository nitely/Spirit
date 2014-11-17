# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import patterns, url


urlpatterns = patterns("spirit.views.admin.comment_flag",
                       url(r'^$', 'flag_open', name='admin-flag'),
                       url(r'^open/$', 'flag_open', name='admin-flag-open'),
                       url(r'^closed/$', 'flag_closed', name='admin-flag-closed'),
                       url(r'^(?P<pk>\d+)/$', 'flag_detail', name='admin-flag-detail'),
                       )
