# -*- coding: utf-8 -*-

from django.conf.urls import re_path, include

from ..core.conf import settings
import spirit.comment.bookmark.urls
import spirit.comment.flag.urls
import spirit.comment.history.urls
import spirit.comment.like.urls
import spirit.comment.poll.urls
from . import views


app_name = 'comment'
urlpatterns = [
    re_path(r'^(?P<topic_id>[0-9]+)/publish/$', views.publish, name='publish'),
    re_path(r'^(?P<topic_id>[0-9]+)/publish/(?P<pk>[0-9]+)/quote/$',
        views.publish,
        name='publish'),

    re_path(r'^(?P<pk>[0-9]+)/update/$', views.update, name='update'),
    re_path(r'^(?P<pk>[0-9]+)/find/$', views.find, name='find'),
    re_path(r'^(?P<topic_id>[0-9]+)/move/$', views.move, name='move'),

    re_path(r'^(?P<pk>[0-9]+)/delete/$', views.delete, name='delete'),
    re_path(r'^(?P<pk>[0-9]+)/undelete/$',
        views.delete,
        kwargs={'remove': False},
        name='undelete'),

    re_path(r'^bookmark/', include(spirit.comment.bookmark.urls)),
    re_path(r'^flag/', include(spirit.comment.flag.urls)),
    re_path(r'^history/', include(spirit.comment.history.urls)),
    re_path(r'^like/', include(spirit.comment.like.urls)),
    re_path(r'^poll/', include(spirit.comment.poll.urls)),
]

if settings.ST_UPLOAD_IMAGE_ENABLED:
    urlpatterns.append(
        re_path(r'^upload/$', views.image_upload_ajax, name='image-upload-ajax'))

if settings.ST_UPLOAD_FILE_ENABLED:
    urlpatterns.append(
        re_path(r'^upload/file/$', views.file_upload_ajax, name='file-upload-ajax'))
