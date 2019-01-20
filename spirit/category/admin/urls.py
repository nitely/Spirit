# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url

from ...core.conf import settings
from . import views


app_name = 'category'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^create/$', views.create, name='create'),
    url(r'^update/(?P<category_id>[0-9]+)/$', views.update, name='update'),
]

if settings.ST_ORDERED_CATEGORIES:
    urlpatterns.extend([
        url(r'^move-up/(?P<category_id>[0-9]+)/$', views.move_up, name='move_up'),
        url(r'^move-dn/(?P<category_id>[0-9]+)/$', views.move_dn, name='move_dn')
    ])
