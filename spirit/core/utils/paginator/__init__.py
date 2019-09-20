# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.paginator import InvalidPage, Paginator
from django.http import Http404
from django.utils.http import urlencode

from infinite_scroll_pagination import paginator
from infinite_scroll_pagination import serializers

from .yt_paginator import YTPaginator, YTPage


def get_page_number(obj_number, per_page):
    if obj_number < per_page:
        return 1
    elif obj_number % per_page:
        return obj_number // per_page + 1
    else:
        return obj_number // per_page


def get_url(url, obj_number, per_page, page_var):
    page = get_page_number(obj_number, per_page)
    data = urlencode({page_var: page, })

    if page == 1:
        return "".join((url, '#c', str(obj_number)))

    return "".join((url, '?', data, '#c', str(obj_number)))


def _paginate(paginator_class, object_list, per_page=15, page_number=None):
    page_number = page_number or 1
    paginator = paginator_class(object_list, per_page)

    try:
        return paginator.page(page_number)
    except InvalidPage as err:
        raise Http404(err)


def paginate(*args, **kwargs):
    return _paginate(Paginator, *args, **kwargs)


# XXX remove
def yt_paginate(*args, **kwargs):
    return _paginate(YTPaginator, *args, **kwargs)


def _seek_serializer(page):
    value, pk = serializers.page_key(page)
    return value, pk, paginator.NEXT_PAGE


def seek_paginate(query_set, page, seek_by, per_page):
    try:
        value, pk, direction = _seek_serializer(page)
    except serializers.InvalidPage:
        raise Http404()
    return paginator.paginate(
        query_set=query_set,
        lookup_field=seek_by,
        value=value,
        pk=pk,
        per_page=per_page,
        move_to=direction)
