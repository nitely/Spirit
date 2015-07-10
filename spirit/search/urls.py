# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from .forms import AdvancedSearchForm
from . import views


urlpatterns = [
    url(r'^$', login_required(views.SearchView(template='spirit/search/search.html', form_class=AdvancedSearchForm)),
        name='search'),
]
