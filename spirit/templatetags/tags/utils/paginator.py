# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from .. import register
from spirit.utils.paginator import paginate, yt_paginate


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
    # TODO: remove
    page_number = page_number or context["request"].GET.get(page_var, 1)
    return yt_paginate(object_list, per_page=per_page, page_number=page_number)


@register.inclusion_tag("spirit/paginator/_yt_paginator.html", takes_context=True)
def render_yt_paginator(context, page, page_var='page', hashtag=''):
    return _render_paginator(context, page, page_var, hashtag)


@register.assignment_tag(takes_context=True)
def paginator_autopaginate(context, object_list, per_page=15, page_var='page', page_number=None):
    # TODO: remove
    page_number = page_number or context["request"].GET.get(page_var, 1)
    return paginate(object_list, per_page=per_page, page_number=page_number)


@register.inclusion_tag("spirit/paginator/_paginator.html", takes_context=True)
def render_paginator(context, page, page_var='page', hashtag=''):
    return _render_paginator(context, page, page_var, hashtag)
