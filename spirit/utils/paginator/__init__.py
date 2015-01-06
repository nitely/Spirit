# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.utils.http import urlencode
from django.http import Http404
from django.core.paginator import Paginator, InvalidPage

from spirit.utils.paginator.yt_paginator import YTPaginator


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


def yt_paginate(*args, **kwargs):
    return _paginate(YTPaginator, *args, **kwargs)
