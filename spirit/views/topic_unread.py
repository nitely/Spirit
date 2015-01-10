# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from spirit.utils.paginator.infinite_paginator import paginate

from spirit.models.topic import Topic


@login_required
def topic_unread_list(request):
    # TODO: add button to clean up read topics? or read all?
    # redirect to first page if empty

    topics = Topic.objects\
        .for_access(user=request.user)\
        .for_unread(user=request.user)\
        .with_bookmarks(user=request.user)

    page = paginate(request, query_set=topics, lookup_field="last_active", page_var='topic_id')
    next_page_pk = None

    if page:
        next_page_pk = page[-1].pk

    context = {
        'page': page,
        'next_page_pk': next_page_pk
    }

    return render(request, 'spirit/topic_unread/list.html', context)
