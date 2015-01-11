# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from haystack.views import SearchView as BaseSearchView

from djconfig import config

from ..utils.paginator import yt_paginate


class SearchView(BaseSearchView):

    def build_page(self):
        paginator = None
        page = yt_paginate(
            self.results,
            per_page=config.topics_per_page,
            page_number=self.request.GET.get('page', 1)
        )
        return paginator, page
