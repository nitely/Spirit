# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.shortcuts import render
from djconfig import config

from spirit.utils.paginator import yt_paginate
from spirit.utils.decorators import administrator_required
from ..models import Topic


@administrator_required
def _index(request, queryset, template):
    topics = yt_paginate(
        queryset,
        per_page=config.topics_per_page,
        page_number=request.GET.get('page', 1)
    )
    context = {'topics': topics, }
    return render(request, template, context)


def deleted(request):
    # Private topics cant be deleted, closed or pinned so we are ok
    return _index(
        request,
        queryset=Topic.objects.filter(is_removed=True),
        template='spirit/topic/admin/deleted.html'
    )


def closed(request):
    return _index(
        request,
        queryset=Topic.objects.filter(is_closed=True),
        template='spirit/topic/admin/closed.html'
    )


def pinned(request):
    return _index(
        request,
        queryset=Topic.objects.filter(is_pinned=True) | Topic.objects.filter(is_globally_pinned=True),
        template='spirit/topic/admin/pinned.html'
    )
