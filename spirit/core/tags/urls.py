# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from .registry import register


@register.simple_tag(takes_context=True)
def to_query_params(context, request=None, **params):
    """
    Adds params to current query string
    """
    # todo: use utils.to_query_params instead
    # todo: test!
    request = request or context['request']
    query_dict = request.GET.copy()  # MultiValueDict >___<

    for k, v in sorted(params.items()):
        query_dict[k] = v

    return query_dict.urlencode()
