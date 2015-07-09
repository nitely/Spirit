# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.http import Http404

from infinite_scroll_pagination.paginator import SeekPaginator, EmptyPage


def paginate(request, query_set, lookup_field, per_page=15, page_var='value'):
    # TODO: remove
    page_pk = request.GET.get(page_var, None)
    paginator = SeekPaginator(query_set, per_page=per_page, lookup_field=lookup_field)

    # First page
    if page_pk is None:
        return paginator.page()

    try:
        obj = query_set.model.objects.get(pk=page_pk)
    except query_set.model.DoesNotExist:
        raise Http404()

    value = getattr(obj, lookup_field)

    try:
        page = paginator.page(value=value, pk=page_pk)
    except EmptyPage:
        raise Http404()

    return page
