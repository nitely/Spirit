# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponsePermanentRedirect
from djconfig import config

from spirit.utils.paginator import paginate, yt_paginate
from spirit.utils.ratelimit.decorators import ratelimit
from ..category.models import Category
from ..comment.models import MOVED
from ..comment.forms import CommentForm
from ..comment.signals import comment_posted
from ..comment.models import Comment
from .poll.forms import TopicPollForm, TopicPollChoiceFormSet
from .moderate.signals import topic_post_moderate
from .models import Topic
from .forms import TopicForm
from .signals import topic_viewed


@login_required
@ratelimit(rate='1/10s')
def publish(request, category_id=None):
    if category_id:
        get_object_or_404(Category.objects.visible(),
                          pk=category_id)

    if request.method == 'POST':
        form = TopicForm(user=request.user, data=request.POST)
        cform = CommentForm(user=request.user, data=request.POST)
        pform = TopicPollForm(data=request.POST)
        pformset = TopicPollChoiceFormSet(can_delete=False, data=request.POST)

        if not request.is_limited and all([form.is_valid(), cform.is_valid(),
                                           pform.is_valid(), pformset.is_valid()]):  # TODO: test!
            # wrap in transaction.atomic?
            topic = form.save()

            cform.topic = topic
            comment = cform.save()
            comment_posted.send(sender=comment.__class__, comment=comment, mentions=cform.mentions)

            # Create a poll only if we have choices
            if pformset.is_filled():
                pform.topic = topic
                poll = pform.save()
                pformset.instance = poll
                pformset.save()

            return redirect(topic.get_absolute_url())
    else:
        form = TopicForm(user=request.user, initial={'category': category_id, })
        cform = CommentForm()
        pform = TopicPollForm()
        pformset = TopicPollChoiceFormSet(can_delete=False)

    context = {
        'form': form,
        'cform': cform,
        'pform': pform,
        'pformset': pformset
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
                topic_post_moderate.send(sender=topic.__class__, user=request.user, topic=topic, action=MOVED)

            return redirect(request.POST.get('next', topic.get_absolute_url()))
    else:
        form = TopicForm(user=request.user, instance=topic)

    context = {'form': form, }

    return render(request, 'spirit/topic/update.html', context)


def detail(request, pk, slug):
    topic = Topic.objects.get_public_or_404(pk, request.user)

    if topic.slug != slug:
        return HttpResponsePermanentRedirect(topic.get_absolute_url())

    topic_viewed.send(sender=topic.__class__, request=request, topic=topic)

    comments = Comment.objects\
        .for_topic(topic=topic)\
        .with_likes(user=request.user)\
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
