# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.utils.http import urlencode


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
