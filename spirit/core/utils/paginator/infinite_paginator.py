# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.http import Http404
from django.shortcuts import get_object_or_404

from infinite_scroll_pagination.paginator import SeekPaginator, EmptyPage


def paginate(request, query_set, lookup_field, per_page=15, page_var='value'):
    # TODO: remove
    value = None
    page_pk = request.GET.get(page_var, None)

    # It's not the first page
    if page_pk is not None:
        obj = get_object_or_404(query_set.model, pk=page_pk)
        value = getattr(obj, lookup_field)

    paginator = SeekPaginator(query_set, per_page=per_page, lookup_field=lookup_field)

    try:
        page = paginator.page(value=value, pk=page_pk)
    except EmptyPage:
        raise Http404()

    return page
