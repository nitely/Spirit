# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.SearchView(), name='search'),
]
