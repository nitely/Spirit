# -*- coding: utf-8 -*-

from django.http import Http404

from infinite_scroll_pagination import paginator
from infinite_scroll_pagination import serializers


def paginate(request, query_set, lookup_field, per_page=15, page_var='value'):
    # TODO: remove
    try:
        value, pk = serializers.page_key(
            request.GET.get(page_var, ''))
    except serializers.InvalidPage:
        return Http404()

    try:
        return paginator.paginate(
            query_set=query_set,
            lookup_field='-' + lookup_field,
            value=value,
            pk=pk,
            per_page=per_page,
            move_to=paginator.NEXT_PAGE)
    except paginator.EmptyPage:
        raise Http404()
