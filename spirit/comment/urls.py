# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url, include

from ..core.conf import settings
import spirit.comment.bookmark.urls
import spirit.comment.flag.urls
import spirit.comment.history.urls
import spirit.comment.like.urls
import spirit.comment.poll.urls
from . import views


app_name = 'comment'
urlpatterns = [
    url(r'^(?P<topic_id>[0-9]+)/publish/$', views.publish, name='publish'),
    url(r'^(?P<topic_id>[0-9]+)/publish/(?P<pk>[0-9]+)/quote/$',
        views.publish,
        name='publish'),

    url(r'^(?P<pk>[0-9]+)/update/$', views.update, name='update'),
    url(r'^(?P<pk>[0-9]+)/find/$', views.find, name='find'),
    url(r'^(?P<topic_id>[0-9]+)/move/$', views.move, name='move'),

    url(r'^(?P<pk>[0-9]+)/delete/$', views.delete, name='delete'),
    url(r'^(?P<pk>[0-9]+)/undelete/$',
        views.delete,
        kwargs={'remove': False},
        name='undelete'),

    url(r'^bookmark/', include(spirit.comment.bookmark.urls)),
    url(r'^flag/', include(spirit.comment.flag.urls)),
    url(r'^history/', include(spirit.comment.history.urls)),
    url(r'^like/', include(spirit.comment.like.urls)),
    url(r'^poll/', include(spirit.comment.poll.urls)),
]

if settings.ST_UPLOAD_IMAGE_ENABLED:
    urlpatterns.append(
        url(r'^upload/$', views.image_upload_ajax, name='image-upload-ajax'))

if settings.ST_UPLOAD_FILE_ENABLED:
    urlpatterns.append(
        url(r'^upload/file/$', views.file_upload_ajax, name='file-upload-ajax'))
