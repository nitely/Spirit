#-*- coding: utf-8 -*-

from django.http import Http404
from django.core.paginator import Paginator, InvalidPage

from .. import register
from spirit.utils.paginator.yt_paginator import YTPaginator


def _get_page(context, object_list, per_page, page_var, page_number, paginator_class):
    request = context["request"]
    page_number = page_number or request.GET.get(page_var, 1)

    paginator = paginator_class(object_list, per_page)

    try:
        page = paginator.page(page_number)
    except InvalidPage as err:
        raise Http404(err)

    return page


def _render_paginator(context, page, page_var, hashtag):
    query_dict = context["request"].GET.copy()

    try:
        del query_dict[page_var]
    except KeyError:
        pass

    extra_query = ""

    if query_dict:
        extra_query = "&%s" % query_dict.urlencode()

    if hashtag:
        hashtag = "#%s" % hashtag

    return {
        "page": page,
        "page_var": page_var,
        "hashtag": hashtag,
        "extra_query": extra_query
    }


@register.assignment_tag(takes_context=True)
def yt_paginator_autopaginate(context, object_list, per_page=15, page_var='page', page_number=None):
    return _get_page(context, object_list, per_page, page_var, page_number, YTPaginator)


@register.inclusion_tag("spirit/paginator/_yt_paginator.html", takes_context=True)
def render_yt_paginator(context, page, page_var='page', hashtag=''):
    return _render_paginator(context, page, page_var, hashtag)


@register.assignment_tag(takes_context=True)
def paginator_autopaginate(context, object_list, per_page=15, page_var='page', page_number=None):
    return _get_page(context, object_list, per_page, page_var, page_number, Paginator)


@register.inclusion_tag("spirit/paginator/_paginator.html", takes_context=True)
def render_paginator(context, page, page_var='page', hashtag=''):
    return _render_paginator(context, page, page_var, hashtag)