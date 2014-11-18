# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import patterns, url


urlpatterns = patterns("spirit.views.comment_flag",
                       url(r'^(?P<comment_id>\d+)/create/$', 'flag_create', name='flag-create'),
                       )
