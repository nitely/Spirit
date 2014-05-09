#-*- coding: utf-8 -*-

from django.conf.urls import patterns, url


urlpatterns = patterns("spirit.views.comment_history",
    url(r'^(?P<comment_id>\d+)/$', 'comment_history_detail', name='comment-history'),
)