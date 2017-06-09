# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import include, url

import spirit.topic.views
import spirit.admin.urls
import spirit.user.urls
import spirit.search.urls
import spirit.category.urls
import spirit.topic.urls
import spirit.comment.urls


patterns = [
    url(r'^$', spirit.topic.views.index_active, name='index'),
    url(r'^st/admin/', include(spirit.admin.urls, namespace='admin')),
    url(r'^user/', include(spirit.user.urls, namespace='user')),
    url(r'^search/', include(spirit.search.urls, namespace='search')),
    url(r'^category/', include(spirit.category.urls, namespace='category')),
    url(r'^topic/', include(spirit.topic.urls, namespace='topic')),
    url(r'^comment/', include(spirit.comment.urls, namespace='comment')),
]


urlpatterns = [
    url(r'^', include(patterns, namespace='spirit', app_name='spirit')),
]
