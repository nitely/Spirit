from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from djconfig import config
from haystack.views import SearchView as BaseSearchView

from ..core.utils.paginator import yt_paginate
from .forms import AdvancedSearchForm


class SearchView(BaseSearchView):
    """
    This view does not pre load data from\
    the database (``load_all=False``),\
    all required fields to display the\
    results must be stored (ie: ``indexed=False``).

    Avoid doing ``{{ result.object }}`` to\
    prevent database hits.
    """

    def __init__(self, *args, **kwargs):  # no-qa
        super().__init__(
            template="spirit/search/search.html",
            form_class=AdvancedSearchForm,
            load_all=False,
        )

    @method_decorator(login_required)
    def __call__(self, request):
        return super().__call__(request)

    def build_page(self):
        paginator = None
        page = yt_paginate(
            self.results,
            per_page=config.topics_per_page,
            page_number=self.request.GET.get("page", 1),
        )
        page = [{"fields": r.get_stored_fields(), "pk": r.pk} for r in page]
        return paginator, page
