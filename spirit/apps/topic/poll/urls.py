# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^update/(?P<pk>\d+)/$', views.poll_update, name='poll-update'),
    url(r'^close/(?P<pk>\d+)/$', views.poll_close, name='poll-close'),
    url(r'^vote/(?P<pk>\d+)/$', views.poll_vote, name='poll-vote'),
]
