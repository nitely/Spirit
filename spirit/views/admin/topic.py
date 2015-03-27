# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.shortcuts import render

from djconfig import config

from ...utils.paginator import yt_paginate
from spirit.utils.decorators import administrator_required
from spirit.models.topic import Topic


@administrator_required
def topic_deleted(request):
    # Private topics cant be deleted, closed or pinned so we are ok
    topics = yt_paginate(
        Topic.objects.filter(is_removed=True),
        per_page=config.topics_per_page,
        page_number=request.GET.get('page', 1)
    )
    context = {'topics': topics, }
    return render(request, 'spirit/admin/topic/topic_deleted.html', context)


@administrator_required
def topic_closed(request):
    topics = yt_paginate(
        Topic.objects.filter(is_closed=True),
        per_page=config.topics_per_page,
        page_number=request.GET.get('page', 1)
    )
    context = {'topics': topics, }
    return render(request, 'spirit/admin/topic/topic_closed.html', context)


@administrator_required
def topic_pinned(request):
    topics = Topic.objects.filter(is_pinned=True) | Topic.objects.filter(is_globally_pinned=True)
    topics = yt_paginate(
        topics,
        per_page=config.topics_per_page,
        page_number=request.GET.get('page', 1)
    )
    context = {'topics': topics, }
    return render(request, 'spirit/admin/topic/topic_pinned.html', context)
