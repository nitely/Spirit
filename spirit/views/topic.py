# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponsePermanentRedirect

from djconfig import config

from ..utils.paginator import paginate, yt_paginate
from ..utils.ratelimit.decorators import ratelimit
from ..models.category import Category
from ..models.comment import MOVED
from ..forms.comment import CommentForm
from ..signals.comment import comment_posted
from ..forms.topic_poll import TopicPollForm, TopicPollChoiceFormSet

from ..models.comment import Comment
from ..models.topic import Topic
from ..forms.topic import TopicForm
from ..signals.topic import topic_viewed
from ..signals.topic_moderate import topic_post_moderate


@login_required
@ratelimit(rate='1/10s')
def topic_publish(request, category_id=None):
    if category_id:
        get_object_or_404(Category.objects.visible(),
                          pk=category_id)

    if request.method == 'POST':
        form = TopicForm(user=request.user, data=request.POST)
        cform = CommentForm(user=request.user, data=request.POST)
        pform = TopicPollForm(data=request.POST)
        pformset = TopicPollChoiceFormSet(can_delete=False, data=request.POST)

        if not request.is_limited and form.is_valid() and cform.is_valid() \
                and pform.is_valid() and pformset.is_valid():
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

    return render(request, 'spirit/topic/topic_publish.html', context)


@login_required
def topic_update(request, pk):
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

    return render(request, 'spirit/topic/topic_update.html', context)


def topic_detail(request, pk, slug):
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

    return render(request, 'spirit/topic/topic_detail.html', context)


def topic_active_list(request):
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

    return render(request, 'spirit/topic/topics_active.html', context)
