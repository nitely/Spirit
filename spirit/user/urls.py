# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url, include

from .auth import urls as auth_urls
from . import views


urlpatterns = [
    url(r'^$', views.update, name='profile-update'),
    url(r'^password-change/$', views.password_change, name='profile-password-change'),
    url(r'^email-change/$', views.email_change, name='profile-email-change'),
    url(r'^email-change/(?P<token>[0-9A-Za-z_\-\.]+)/$', views.email_change_confirm, name='email-change-confirm'),

    url(r'^(?P<pk>\d+)/$', views.comments, kwargs={'slug': "", }, name='profile-detail'),
    url(r'^(?P<pk>\d+)/(?P<slug>[\w-]+)/$', views.comments, name='profile-detail'),

    url(r'^topics/(?P<pk>\d+)/$', views.topics, kwargs={'slug': "", }, name='profile-topics'),
    url(r'^topics/(?P<pk>\d+)/(?P<slug>[\w-]+)/$', views.topics, name='profile-topics'),

    url(r'^likes/(?P<pk>\d+)/$', views.likes, kwargs={'slug': "", }, name='profile-likes'),
    url(r'^likes/(?P<pk>\d+)/(?P<slug>[\w-]+)/$', views.likes, name='profile-likes'),

    url(r'^menu/$', views.menu, name='user-menu'),
]

urlpatterns += [
    url(r'^', include(auth_urls)),
]