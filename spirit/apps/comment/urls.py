# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^(?P<topic_id>\d+)/publish/$', views.publish, name='comment-publish'),
    url(r'^(?P<topic_id>\d+)/publish/(?P<pk>\d+)/quote/$', views.publish, name='comment-publish'),

    url(r'^(?P<pk>\d+)/update/$', views.update, name='comment-update'),
    url(r'^(?P<pk>\d+)/find/$', views.find, name='comment-find'),
    url(r'^(?P<topic_id>\d+)/move/$', views.move, name='comment-move'),

    url(r'^(?P<pk>\d+)/delete/$', views.delete, name='comment-delete'),
    url(r'^(?P<pk>\d+)/undelete/$', views.delete, kwargs={'remove': False, }, name='comment-undelete'),

    url(r'^upload/$', views.image_upload_ajax, name='comment-image-upload-ajax'),
]
