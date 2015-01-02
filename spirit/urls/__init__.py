# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import patterns, include, url


urls = patterns('',
                url(r'^$', 'spirit.views.topic.topic_active_list', name='index'),
                url(r'^st/admin/', include('spirit.urls.admin')),
                url(r'^category/', include('spirit.urls.category')),
                url(r'^topic/', include('spirit.urls.topic')),
                url(r'^topic/moderate/', include('spirit.urls.topic_moderate')),
                url(r'^topic/unread/', include('spirit.urls.topic_unread')),
                url(r'^topic/notification/', include('spirit.urls.topic_notification')),
                url(r'^topic/favorite/', include('spirit.urls.topic_favorite')),
                url(r'^topic/private/', include('spirit.urls.topic_private')),
                url(r'^topic/poll/', include('spirit.urls.topic_poll')),
                url(r'^comment/', include('spirit.urls.comment')),
                url(r'^comment/bookmark/', include('spirit.urls.comment_bookmark')),
                url(r'^comment/flag/', include('spirit.urls.comment_flag')),
                url(r'^comment/history/', include('spirit.urls.comment_history')),
                url(r'^comment/like/', include('spirit.urls.comment_like')),
                url(r'^user/', include('spirit.urls.user')),
                url(r'^search/', include('spirit.urls.search')),
                )

urlpatterns = patterns('', url(r'^', include(urls, namespace="spirit", app_name="spirit")))
