# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^(?P<topic_id>\d+)/publish/$', views.comment_publish, name='comment-publish'),
    url(r'^(?P<topic_id>\d+)/publish/(?P<pk>\d+)/quote/$', views.comment_publish, name='comment-publish'),

    url(r'^(?P<pk>\d+)/update/$', views.comment_update, name='comment-update'),
    url(r'^(?P<pk>\d+)/find/$', views.comment_find, name='comment-find'),
    url(r'^(?P<topic_id>\d+)/move/$', views.comment_move, name='comment-move'),

    url(r'^(?P<pk>\d+)/delete/$', views.comment_delete, name='comment-delete'),
    url(r'^(?P<pk>\d+)/undelete/$', views.comment_delete, kwargs={'remove': False, }, name='comment-undelete'),

    url(r'^upload/$', views.comment_image_upload_ajax, name='comment-image-upload-ajax'),
]
