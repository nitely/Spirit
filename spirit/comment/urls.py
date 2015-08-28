# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url, include

import spirit.comment.bookmark.urls
import spirit.comment.flag.urls
import spirit.comment.history.urls
import spirit.comment.like.urls
import spirit.comment.poll.urls
from . import views


urlpatterns = [
    url(r'^(?P<topic_id>\d+)/publish/$', views.publish, name='publish'),
    url(r'^(?P<topic_id>\d+)/publish/(?P<pk>\d+)/quote/$', views.publish, name='publish'),

    url(r'^(?P<pk>\d+)/update/$', views.update, name='update'),
    url(r'^(?P<pk>\d+)/find/$', views.find, name='find'),
    url(r'^(?P<topic_id>\d+)/move/$', views.move, name='move'),

    url(r'^(?P<pk>\d+)/delete/$', views.delete, name='delete'),
    url(r'^(?P<pk>\d+)/undelete/$', views.delete, kwargs={'remove': False, }, name='undelete'),

    url(r'^upload/$', views.image_upload_ajax, name='image-upload-ajax'),

    url(r'^bookmark/', include(spirit.comment.bookmark.urls, namespace='bookmark')),
    url(r'^flag/', include(spirit.comment.flag.urls, namespace='flag')),
    url(r'^history/', include(spirit.comment.history.urls, namespace='history')),
    url(r'^like/', include(spirit.comment.like.urls, namespace='like')),
    url(r'^poll/', include(spirit.comment.poll.urls, namespace='poll')),
]
