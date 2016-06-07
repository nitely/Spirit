# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from haystack.views import SearchView as BaseSearchView
from djconfig import config

from .forms import AdvancedSearchForm
from ..core.utils.paginator import yt_paginate


class SearchView(BaseSearchView):
    """
    This view does not pre load data fom\
    the database (``load_all=False``),\
    all required fields to display the\
    results must be stored (ie: ``indexed=False``).

    Avoid doing ``{{ result.object }}`` to\
    prevent database hits.
    """
    def __init__(self, *_args, **_kwargs):  # no-qa
        super(SearchView, self).__init__(
            template='spirit/search/search.html',
            form_class=AdvancedSearchForm,
            load_all=False)

    def build_page(self):
        paginator = None
        page = yt_paginate(
            self.results,
            per_page=config.topics_per_page,
            page_number=self.request.GET.get('page', 1))
        return paginator, page
