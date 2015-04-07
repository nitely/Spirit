# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import patterns, include, url


urls = patterns(
    '',

    url(r'^$', 'spirit.apps.topic.views.topic_active_list', name='index'),
    url(r'^st/admin/', include('spirit.apps.admin.urls')),
    url(r'^category/', include('spirit.apps.category.urls')),
    url(r'^topic/', include('spirit.apps.topic.urls')),
    url(r'^topic/moderate/', include('spirit.apps.topic.moderate.urls')),
    url(r'^topic/unread/', include('spirit.apps.topic.unread.urls')),
    url(r'^topic/notification/', include('spirit.apps.topic.notification.urls')),
    url(r'^topic/favorite/', include('spirit.apps.topic.favorite.urls')),
    url(r'^topic/private/', include('spirit.apps.topic.private.urls')),
    url(r'^topic/poll/', include('spirit.apps.topic.poll.urls')),
    url(r'^comment/', include('spirit.apps.comment.urls')),
    url(r'^comment/bookmark/', include('spirit.apps.comment.bookmark.urls')),
    url(r'^comment/flag/', include('spirit.apps.comment.flag.urls')),
    url(r'^comment/history/', include('spirit.apps.comment.history.urls')),
    url(r'^comment/like/', include('spirit.apps.comment.like.urls')),
    url(r'^user/', include('spirit.apps.user.urls')),
    url(r'^search/', include('spirit.apps.search.urls')),
    )

urlpatterns = patterns('', url(r'^', include(urls, namespace="spirit", app_name="spirit")))
