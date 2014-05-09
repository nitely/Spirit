#-*- coding: utf-8 -*-

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from spirit.utils.paginator.infinite_paginator import paginate

from spirit.models.topic import Topic


@login_required
def topic_unread_list(request):
    # TODO: add button to clean up read topics? or read all?
    # redirect to first page if empty

    topics = Topic.objects.for_access(request.user)\
        .filter(topicunread__user=request.user,
                topicunread__is_read=False)

    page = paginate(request, query_set=topics, lookup_field="last_active", page_var='topic_id')
    next_page_pk = None

    if page:
        next_page_pk = page[-1].pk

    return render(request, 'spirit/topic_unread/list.html', {'page': page,
                                                             'next_page_pk': next_page_pk})