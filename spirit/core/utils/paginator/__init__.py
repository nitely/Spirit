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
    direction = paginator.NEXT_PAGE
    if page.startswith('-'):
        direction = paginator.PREV_PAGE
        page = page[1:]
    value, pk = serializers.page_key(page)
    return value, pk, direction

def seek_paginate(query_set, seek_by, page_param, per_page):
    try:
        value, pk, direction = _seek_serializer(page_param)
    except serializers.InvalidPage:
        raise Http404()
    try:
        page = paginator.paginate(
            query_set=query_set,
            lookup_field=seek_by,
            value=value,
            pk=pk,
            per_page=per_page,
            move_to=direction)
    except paginator.EmptyPage:
        if not page_param:  # first page
            return query_set.none()
        raise Http404()
    page.prev_page_key = '-' + serializers.to_page_key(**page.prev_page())
    page.next_page_key = serializers.to_page_key(**page.next_page())
    # We do an extra query to fetch a complete
    # first page when navigating backwards (prev page).
    # It may contain records of the second page,
    # but otherwise we would see a few
    # records, maybe even just one (new) record and that'd
    # look weird
    #is_bw_first_page = (
    #    direction == paginator.PREV_PAGE
    #    and len(page) < per_page
    #    and not page.has_previous())
    #if is_bw_first_page:
    #    page = paginator.paginate(
    #        query_set=query_set,
    #        lookup_field=seek_by,
    #        value=None,
    #        pk=None,
    #        per_page=per_page)
    return page
