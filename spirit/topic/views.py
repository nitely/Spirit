# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils import timezone

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


@login_required
@ratelimit(rate='1/10s')
def publish(request, category_id=None):
    if category_id:
        get_object_or_404(
            Category.objects.visible(),
            pk=category_id)

    user = request.user

    if request.method == 'POST':
        form = TopicForm(user=user, data=request.POST)
        cform = CommentForm(user=user, data=request.POST)

        if (all([form.is_valid(), cform.is_valid()]) and
                not request.is_limited()):
            if not user.st.update_post_hash(form.get_topic_hash()):
                return redirect(
                    request.POST.get('next', None) or
                    form.get_category().get_absolute_url())

            # wrap in transaction.atomic?
            topic = form.save()
            cform.topic = topic
            comment = cform.save()
            comment_posted(comment=comment, mentions=cform.mentions)
            return redirect(topic.get_absolute_url())
    else:
        form = TopicForm(user=user, initial={'category': category_id})
        cform = CommentForm()

    context = {
        'form': form,
        'cform': cform,
    }

    return render(request, 'spirit/topic/publish.html', context)


@login_required
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

    context = {
        'form': form,
    }

    return render(request, 'spirit/topic/update.html', context)


def detail(request, pk, slug):
    topic = Topic.objects.get_public_or_404(pk, request.user)

    if topic.slug != slug:
        return HttpResponsePermanentRedirect(topic.get_absolute_url())

    utils.topic_viewed(request=request, topic=topic)

    comment = Comment.objects.for_topic(topic=topic).order_by('date')[:1]

    comments = Comment.objects\
        .exclude(id=comment[0].id)\
        .for_topic(topic=topic)\
        .with_likes(user=request.user)\
        .with_polls(user=request.user)\
        .order_by('-likes_count', 'date')

    counts = Comment.objects\
        .exclude(id=comment[0].id)\
        .for_topic(topic=topic)\
        .with_likes(user=request.user)\
        .with_polls(user=request.user)\
        .count()

    comments = paginate(
        comments,
        per_page=config.comments_per_page,
        page_number=request.GET.get('page', 1)
    )

    context = {
        'topic': topic,
        'count': counts,
        'first_content': comment,
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
        .order_by('-is_top', '-is_globally_pinned', '-last_active')\
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


@login_required
def is_top(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)
    topic.is_top = True
    topic.last_active = timezone.now()
    topic.save()
    return HttpResponseRedirect(reverse('spirit:topic:detail', kwargs={'pk': topic_id}))

@login_required
def no_top(request, pk):
    topic = get_object_or_404(Topic, pk=pk)
    topic.is_top = False
    topic.last_active = timezone.now()
    topic.save()
    return HttpResponseRedirect(reverse('spirit:topic:detail', kwargs={'pk': pk}))
