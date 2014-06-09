#-*- coding: utf-8 -*-

from haystack.views import SearchView as BaseSearchView


class SearchView(BaseSearchView):

    def build_page(self):
        paginator = None
        page = self.results
        return paginator, page