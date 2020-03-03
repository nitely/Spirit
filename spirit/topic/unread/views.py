# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from infinite_scroll_pagination.serializers import to_page_key

from ...core.utils.paginator.infinite_paginator import paginate
from ..models import Topic


@login_required
def index(request):
    # TODO: add button to clean up read topics? or read all?
    # redirect to first page if empty

    topics = (
        Topic.objects
        .for_access(user=request.user)
        .for_unread(user=request.user)
        .with_bookmarks(user=request.user))
    page = paginate(
        request,
        query_set=topics,
        lookup_field="last_active",
        page_var='p')

    context = {
        'page': page,
        'next_page': to_page_key(**page.next_page())
    }

    return render(request, 'spirit/topic/unread/index.html', context)
