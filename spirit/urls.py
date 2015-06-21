# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import include, url

import spirit.apps.topic.views
import spirit.apps.admin.urls
import spirit.apps.user.urls
import spirit.apps.search.urls
import spirit.apps.category.urls
import spirit.apps.topic.urls
import spirit.apps.topic.moderate.urls
import spirit.apps.topic.unread.urls
import spirit.apps.topic.notification.urls
import spirit.apps.topic.favorite.urls
import spirit.apps.topic.private.urls
import spirit.apps.topic.poll.urls
import spirit.apps.comment.urls
import spirit.apps.comment.bookmark.urls
import spirit.apps.comment.flag.urls
import spirit.apps.comment.history.urls
import spirit.apps.comment.like.urls


pattern_list = [
    url(r'^$', spirit.apps.topic.views.index_active, name='index'),
    url(r'^st/admin/', include(spirit.apps.admin.urls)),
    url(r'^user/', include(spirit.apps.user.urls)),
    url(r'^search/', include(spirit.apps.search.urls)),
    url(r'^category/', include(spirit.apps.category.urls)),

    url(r'^topic/', include(spirit.apps.topic.urls)),
    url(r'^topic/moderate/', include(spirit.apps.topic.moderate.urls)),
    url(r'^topic/unread/', include(spirit.apps.topic.unread.urls)),
    url(r'^topic/notification/', include(spirit.apps.topic.notification.urls)),
    url(r'^topic/favorite/', include(spirit.apps.topic.favorite.urls)),
    url(r'^topic/private/', include(spirit.apps.topic.private.urls)),
    url(r'^topic/poll/', include(spirit.apps.topic.poll.urls)),

    url(r'^comment/', include(spirit.apps.comment.urls)),
    url(r'^comment/bookmark/', include(spirit.apps.comment.bookmark.urls)),
    url(r'^comment/flag/', include(spirit.apps.comment.flag.urls)),
    url(r'^comment/history/', include(spirit.apps.comment.history.urls)),
    url(r'^comment/like/', include(spirit.apps.comment.like.urls)),
]


urlpatterns = [
    url(r'^', include(pattern_list, namespace="spirit", app_name="spirit")),
]
