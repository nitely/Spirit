# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import patterns, url


urlpatterns = patterns("spirit.views.comment",
                       url(r'^(?P<topic_id>\d+)/publish/$', 'comment_publish', name='comment-publish'),
                       url(r'^(?P<topic_id>\d+)/publish/(?P<pk>\d+)/quote/$',
                           'comment_publish',
                           name='comment-publish'),

                       url(r'^(?P<pk>\d+)/update/$', 'comment_update', name='comment-update'),
                       url(r'^(?P<pk>\d+)/find/$', 'comment_find', name='comment-find'),
                       url(r'^(?P<topic_id>\d+)/move/$', 'comment_move', name='comment-move'),

                       url(r'^(?P<pk>\d+)/delete/$', 'comment_delete', name='comment-delete'),
                       url(r'^(?P<pk>\d+)/undelete/$',
                           'comment_delete',
                           kwargs={'remove': False, }, name='comment-undelete'),

                       url(r'^upload/$', 'comment_image_upload_ajax', name='comment-image-upload-ajax'),
                       )
