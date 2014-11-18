# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from ..views.search import SearchView
from ..forms.search import AdvancedSearchForm


urlpatterns = patterns("",
                       url(r'^$', login_required(SearchView(
                           template='spirit/search/search.html',
                           form_class=AdvancedSearchForm
                           )), name='search'),
                       )
