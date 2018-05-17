# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url, include

import spirit.topic.moderate.urls
import spirit.topic.unread.urls
import spirit.topic.notification.urls
import spirit.topic.favorite.urls
import spirit.topic.private.urls
from . import views


urlpatterns = [
    url(r'^publish/$', views.publish, name='publish'),
    url(r'^publish/(?P<category_id>[0-9]+)/$', views.publish, name='publish'),

    url(r'^update/(?P<pk>[0-9]+)/$', views.update, name='update'),

    url(r'^(?P<topic_id>[0-9]+)/top/$', views.is_top, name='top'),
    url(r'^(?P<pk>[0-9]+)/notop/$', views.no_top, name='no-top'),

    url(r'^(?P<pk>[0-9]+)/$', views.detail, kwargs={'slug': "", }, name='detail'),
    url(r'^(?P<pk>[0-9]+)/(?P<slug>[\w-]+)/$', views.detail, name='detail'),

    url(r'^active/$', views.index_active, name='index-active'),

    url(r'^moderate/', include(spirit.topic.moderate.urls, namespace='moderate')),
    url(r'^unread/', include(spirit.topic.unread.urls, namespace='unread')),
    url(r'^notification/', include(spirit.topic.notification.urls, namespace='notification')),
    url(r'^favorite/', include(spirit.topic.favorite.urls, namespace='favorite')),
    url(r'^private/', include(spirit.topic.private.urls, namespace='private')),
]
