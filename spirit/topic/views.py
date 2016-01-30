# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponsePermanentRedirect

from djconfig import config

from ..core.utils.paginator import paginate, yt_paginate
from ..core.utils.ratelimit.decorators import ratelimit
from ..category.models import Category
from ..comment.models import MOVED
from ..comment.forms import CommentForm
from ..comment.utils import comment_posted
from ..comment.models import Comment
from .models import Topic
from .forms import TopicForm
from . import utils

from trusts.decorators import permission_required

@login_required
@permission_required('spirit_category.add_topic_for_category', fieldlookups_kwargs={'pk': 'category_id'})
@ratelimit(rate='1/10s')
def publish(request, category_id=None):
    if category_id:
        get_object_or_404(Category.objects.visible(),
                          pk=category_id)

    if request.method == 'POST':
        form = TopicForm(user=request.user, data=request.POST)
        cform = CommentForm(user=request.user, data=request.POST)

        if not request.is_limited and all([form.is_valid(), cform.is_valid()]):  # TODO: test!
            # wrap in transaction.atomic?
            topic = form.save()
            cform.topic = topic
            comment = cform.save()
            comment_posted(comment=comment, mentions=cform.mentions)
            return redirect(topic.get_absolute_url())
    else:
        form = TopicForm(user=request.user, initial={'category': category_id, })
        cform = CommentForm()

    context = {
        'form': form,
        'cform': cform
    }

    return render(request, 'spirit/topic/publish.html', context)


@login_required
@permission_required('spirit_topic.change_topic', fieldlookups_kwargs={'pk': 'pk'})
def update(request, pk):
    topic = Topic.objects.for_update_or_404(pk, request.user)

    if request.method == 'POST':
        form = TopicForm(user=request.user, data=request.POST, instance=topic)
        category_id = topic.category_id

        if form.is_valid():
            topic = form.save()

            if topic.category_id != category_id:
                Comment.create_moderation_action(user=request.user, topic=topic, action=MOVED)

            return redirect(request.POST.get('next', topic.get_absolute_url()))
    else:
        form = TopicForm(user=request.user, instance=topic)

    context = {'form': form, }

    return render(request, 'spirit/topic/update.html', context)


@permission_required('spirit_topic.read_topic', fieldlookups_kwargs={'pk': 'pk'})
def detail(request, pk, slug):
    topic = Topic.objects.get_public_or_404(pk, request.user)

    if topic.slug != slug:
        return HttpResponsePermanentRedirect(topic.get_absolute_url())

    utils.topic_viewed(request=request, topic=topic)

    comments = Comment.objects\
        .for_topic(topic=topic)\
        .with_likes(user=request.user)\
        .with_polls(user=request.user)\
        .order_by('date')

    comments = paginate(
        comments,
        per_page=config.comments_per_page,
        page_number=request.GET.get('page', 1)
    )

    context = {
        'topic': topic,
        'comments': comments
    }

    return render(request, 'spirit/topic/detail.html', context)


def index_active(request):
    categories = Category.objects\
        .visible()\
        .parents()

    topics = Topic.objects\
        .visible()\
        .global_()\
        .with_bookmarks(user=request.user)\
        .order_by('-is_globally_pinned', '-last_active')\
        .select_related('category')

    topics = yt_paginate(
        topics,
        per_page=config.topics_per_page,
        page_number=request.GET.get('page', 1)
    )

    context = {
        'categories': categories,
        'topics': topics
    }

    return render(request, 'spirit/topic/active.html', context)
