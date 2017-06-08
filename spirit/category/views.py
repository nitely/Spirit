# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.views.generic import ListView
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponsePermanentRedirect

from djconfig import config

from ..core.utils.paginator import yt_paginate
from ..topic.models import Topic
from .models import Category


def detail(request, pk, slug, course_no):
    category = get_object_or_404(Category.objects.visible(),
                                 pk=pk)
    print("hi")
    print(course_no)

    if category.slug != slug:
        return HttpResponsePermanentRedirect(category.get_absolute_url())

    subcategories = Category.objects\
        .visible()\
        .children(parent=category)

    topics = Topic.objects\
        .unremoved()\
        .with_bookmarks(user=request.user)\
        .for_category(category=category)\
        .order_by('-is_globally_pinned', '-is_pinned', '-last_active')\
        .select_related('category')

    if course_no:
        topics = topics.filter(course_no=course_no)

    topics = yt_paginate(
        topics,
        per_page=config.topics_per_page,
        page_number=request.GET.get('page', 1)
    )

    context = {
        'category': category,
        'subcategories': subcategories,
        'topics': topics
    }

    return render(request, 'spirit/category/detail.html', context)


class IndexView(ListView):

    template_name = 'spirit/category/index.html'
    context_object_name = "categories"
    queryset = Category.objects.visible().parents()
