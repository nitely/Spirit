# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url, include

import spirit.topic.moderate.urls
import spirit.topic.unread.urls
import spirit.topic.notification.urls
import spirit.topic.favorite.urls
import spirit.topic.private.urls
import spirit.topic.poll.urls
from . import views


urlpatterns = [
    url(r'^publish/$', views.publish, name='publish'),
    url(r'^publish/(?P<category_id>\d+)/$', views.publish, name='publish'),

    url(r'^update/(?P<pk>\d+)/$', views.update, name='update'),

    url(r'^(?P<pk>\d+)/$', views.detail, kwargs={'slug': "", }, name='detail'),
    url(r'^(?P<pk>\d+)/(?P<slug>[\w-]+)/$', views.detail, name='detail'),

    url(r'^active/$', views.index_active, name='index-active'),

    url(r'^moderate/', include(spirit.topic.moderate.urls, namespace='moderate')),
    url(r'^unread/', include(spirit.topic.unread.urls, namespace='unread')),
    url(r'^notification/', include(spirit.topic.notification.urls, namespace='notification')),
    url(r'^favorite/', include(spirit.topic.favorite.urls, namespace='favorite')),
    url(r'^private/', include(spirit.topic.private.urls, namespace='private')),
    url(r'^poll/', include(spirit.topic.poll.urls, namespace='poll')),  # todo: remove me!
]
