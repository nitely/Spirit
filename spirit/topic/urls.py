# -*- coding: utf-8 -*-

from django.conf.urls import re_path, include

import spirit.topic.moderate.urls
import spirit.topic.unread.urls
import spirit.topic.notification.urls
import spirit.topic.favorite.urls
import spirit.topic.private.urls
from . import views


app_name = 'topic'
urlpatterns = [
    re_path(r'^publish/$', views.publish, name='publish'),
    re_path(r'^publish/(?P<category_id>[0-9]+)/$', views.publish, name='publish'),

    re_path(r'^update/(?P<pk>[0-9]+)/$', views.update, name='update'),

    re_path(r'^(?P<pk>[0-9]+)/$', views.detail, kwargs={'slug': "", }, name='detail'),
    re_path(r'^(?P<pk>[0-9]+)/(?P<slug>[\w-]+)/$', views.detail, name='detail'),

    re_path(r'^active/$', views.index_active, name='index-active'),

    re_path(r'^moderate/', include(spirit.topic.moderate.urls)),
    re_path(r'^unread/', include(spirit.topic.unread.urls)),
    re_path(r'^notification/', include(spirit.topic.notification.urls)),
    re_path(r'^favorite/', include(spirit.topic.favorite.urls)),
    re_path(r'^private/', include(spirit.topic.private.urls))
]
