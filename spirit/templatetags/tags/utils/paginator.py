# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.template.loader import render_to_string
from django.core.paginator import Page

from .. import register
from spirit.utils.paginator import paginate, yt_paginate


def _render_paginator(template, context, page, page_var, hashtag):
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

    context = {
        "page": page,
        "page_var": page_var,
        "hashtag": hashtag,
        "extra_query": extra_query
    }

    return render_to_string(template, context)


@register.assignment_tag(takes_context=True)
def yt_paginator_autopaginate(context, object_list, per_page=15, page_var='page', page_number=None):
    # TODO: remove
    page_number = page_number or context["request"].GET.get(page_var, 1)
    return yt_paginate(object_list, per_page=per_page, page_number=page_number)


@register.assignment_tag(takes_context=True)
def paginator_autopaginate(context, object_list, per_page=15, page_var='page', page_number=None):
    # TODO: remove
    page_number = page_number or context["request"].GET.get(page_var, 1)
    return paginate(object_list, per_page=per_page, page_number=page_number)


@register.simple_tag(takes_context=True)
def render_paginator(context, page, page_var='page', hashtag=''):
    # TODO: test!
    if isinstance(page, Page):
        template = "spirit/paginator/_paginator.html"
    else:
        template = "spirit/paginator/_yt_paginator.html"

    return _render_paginator(template, context, page, page_var, hashtag)
