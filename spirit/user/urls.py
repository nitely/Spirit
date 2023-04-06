# -*- coding: utf-8 -*-

from django.urls import re_path, include

from .auth import urls as auth_urls
from . import views


app_name = 'user'
urlpatterns = [
    re_path(r'^$', views.update, name='update'),
    re_path(r'^password-change/$', views.password_change, name='password-change'),
    re_path(r'^email-change/$', views.email_change, name='email-change'),
    re_path(r'^email-change/(?P<token>[0-9A-Za-z_\-\.]+)/$',
        views.email_change_confirm,
        name='email-change-confirm'),
    re_path(r'^unsubscribe/(?P<pk>[0-9]+)/(?P<token>[0-9A-Za-z_\-\.]+)/$',
        views.unsubscribe, name='unsubscribe'),

    re_path(r'^(?P<pk>[0-9]+)/$', views.comments, kwargs={'slug': ""}, name='detail'),
    re_path(r'^(?P<pk>[0-9]+)/(?P<slug>[\w-]+)/$', views.comments, name='detail'),

    re_path(r'^topics/(?P<pk>[0-9]+)/$', views.topics, kwargs={'slug': ""}, name='topics'),
    re_path(r'^topics/(?P<pk>[0-9]+)/(?P<slug>[\w-]+)/$', views.topics, name='topics'),

    re_path(r'^likes/(?P<pk>[0-9]+)/$', views.likes, kwargs={'slug': ""}, name='likes'),
    re_path(r'^likes/(?P<pk>[0-9]+)/(?P<slug>[\w-]+)/$', views.likes, name='likes'),

    re_path(r'^menu/$', views.menu, name='menu'),

    re_path(r'^', include(auth_urls)),
]
