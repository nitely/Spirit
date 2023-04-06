# -*- coding: utf-8 -*-

from django.urls import include, re_path

import spirit.topic.views
import spirit.admin.urls
import spirit.user.urls
import spirit.search.urls
import spirit.category.urls
import spirit.topic.urls
import spirit.comment.urls


app_name = 'spirit'
urlpatterns = [
    re_path(r'^$', spirit.topic.views.index_active, name='index'),
    re_path(r'^st/admin/', include(spirit.admin.urls)),
    re_path(r'^user/', include(spirit.user.urls)),
    re_path(r'^search/', include(spirit.search.urls)),
    re_path(r'^category/', include(spirit.category.urls)),
    re_path(r'^topic/', include(spirit.topic.urls)),
    re_path(r'^comment/', include(spirit.comment.urls)),
]
