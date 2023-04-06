# -*- coding: utf-8 -*-

from django.urls import re_path

from . import views


app_name = 'search'
urlpatterns = [
    re_path(r'^$', views.SearchView(), name='search'),
]
