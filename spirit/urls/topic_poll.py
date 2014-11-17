# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import patterns, url


urlpatterns = patterns("spirit.views.topic_poll",
                       url(r'^update/(?P<pk>\d+)/$', 'poll_update', name='poll-update'),
                       url(r'^close/(?P<pk>\d+)/$', 'poll_close', name='poll-close'),
                       url(r'^vote/(?P<pk>\d+)/$', 'poll_vote', name='poll-vote'),
                       )
