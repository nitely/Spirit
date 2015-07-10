# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import include, url

import spirit.topic.views
import spirit.admin.urls
import spirit.user.urls
import spirit.search.urls
import spirit.category.urls
import spirit.topic.urls
import spirit.topic.moderate.urls
import spirit.topic.unread.urls
import spirit.topic.notification.urls
import spirit.topic.favorite.urls
import spirit.topic.private.urls
import spirit.topic.poll.urls
import spirit.comment.urls
import spirit.comment.bookmark.urls
import spirit.comment.flag.urls
import spirit.comment.history.urls
import spirit.comment.like.urls


pattern_list = [
    url(r'^$', spirit.topic.views.index_active, name='index'),
    url(r'^st/admin/', include(spirit.admin.urls)),
    url(r'^user/', include(spirit.user.urls)),
    url(r'^search/', include(spirit.search.urls)),
    url(r'^category/', include(spirit.category.urls)),

    url(r'^topic/', include(spirit.topic.urls)),
    url(r'^topic/moderate/', include(spirit.topic.moderate.urls)),
    url(r'^topic/unread/', include(spirit.topic.unread.urls)),
    url(r'^topic/notification/', include(spirit.topic.notification.urls)),
    url(r'^topic/favorite/', include(spirit.topic.favorite.urls)),
    url(r'^topic/private/', include(spirit.topic.private.urls)),
    url(r'^topic/poll/', include(spirit.topic.poll.urls)),

    url(r'^comment/', include(spirit.comment.urls)),
    url(r'^comment/bookmark/', include(spirit.comment.bookmark.urls)),
    url(r'^comment/flag/', include(spirit.comment.flag.urls)),
    url(r'^comment/history/', include(spirit.comment.history.urls)),
    url(r'^comment/like/', include(spirit.comment.like.urls)),
]


urlpatterns = [
    url(r'^', include(pattern_list, namespace="spirit", app_name="spirit")),
]
