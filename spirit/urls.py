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


app_name = 'spirit'
urlpatterns = [
    url(r'^$', spirit.topic.views.index_active, name='index'),
    url(r'^st/admin/', include(spirit.admin.urls)),
    url(r'^user/', include(spirit.user.urls)),
    url(r'^search/', include(spirit.search.urls)),
    url(r'^category/', include(spirit.category.urls)),
    url(r'^topic/', include(spirit.topic.urls)),
    url(r'^comment/', include(spirit.comment.urls)),
]
