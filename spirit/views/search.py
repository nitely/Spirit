# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from haystack.views import SearchView as BaseSearchView


class SearchView(BaseSearchView):

    def build_page(self):
        paginator = None
        page = self.results
        return paginator, page
