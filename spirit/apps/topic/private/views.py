# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import HttpResponsePermanentRedirect
from django.conf import settings
from djconfig import config

from spirit import utils
from spirit.utils.paginator import paginate, yt_paginate
from spirit.utils.ratelimit.decorators import ratelimit
from ...comment.forms import CommentForm
from ...comment.signals import comment_posted
from ...comment.models import Comment
from ..models import Topic
from ..signals import topic_viewed
from .models import TopicPrivate
from .forms import TopicPrivateManyForm, TopicForPrivateForm,\
    TopicPrivateJoinForm, TopicPrivateInviteForm
from .signals import topic_private_post_create, topic_private_access_pre_create


User = get_user_model()


@login_required
@ratelimit(rate='1/10s')
def publish(request, user_id=None):
    if request.method == 'POST':
        tform = TopicForPrivateForm(user=request.user, data=request.POST)
        cform = CommentForm(user=request.user, data=request.POST)
        tpform = TopicPrivateManyForm(user=request.user, data=request.POST)

        if not request.is_limited and all([tform.is_valid(), cform.is_valid(), tpform.is_valid()]):  # TODO: test!
            # wrap in transaction.atomic?
            topic = tform.save()
            cform.topic = topic
            comment = cform.save()
            comment_posted.send(sender=comment.__class__, comment=comment, mentions=None)
            tpform.topic = topic
            topics_private = tpform.save_m2m()
            topic_private_post_create.send(sender=TopicPrivate, topics_private=topics_private, comment=comment)
            return redirect(topic.get_absolute_url())
    else:
        tform = TopicForPrivateForm()
        cform = CommentForm()
        initial = None

        if user_id:
            user = get_object_or_404(User, pk=user_id)
            initial = {'users': [user.username, ]}

        tpform = TopicPrivateManyForm(initial=initial)

    context = {
        'tform': tform,
        'cform': cform,
        'tpform': tpform
    }

    return render(request, 'spirit/topic/private/publish.html', context)


@login_required
def detail(request, topic_id, slug):
    topic_private = get_object_or_404(TopicPrivate.objects.select_related('topic'),
                                      topic_id=topic_id,
                                      user=request.user)
    topic = topic_private.topic

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
        'topic_private': topic_private,
        'comments': comments,
    }

    return render(request, 'spirit/topic/private/detail.html', context)


@login_required
@require_POST
def create_access(request, topic_id):
    topic_private = TopicPrivate.objects.for_create_or_404(topic_id, request.user)
    form = TopicPrivateInviteForm(topic=topic_private.topic, data=request.POST)

    if form.is_valid():
        topic_private_access_pre_create.send(sender=topic_private.__class__,
                                             topic=topic_private.topic,
                                             user=form.cleaned_data['user'])
        form.save()
    else:
        messages.error(request, utils.render_form_errors(form))

    return redirect(request.POST.get('next', topic_private.get_absolute_url()))


@login_required
def delete_access(request, pk):
    topic_private = TopicPrivate.objects.for_delete_or_404(pk, request.user)

    if request.method == 'POST':
        topic_private.delete()

        if request.user.pk == topic_private.user_id:
            return redirect(reverse("spirit:private-list"))

        return redirect(request.POST.get('next', topic_private.get_absolute_url()))

    context = {'topic_private': topic_private, }

    return render(request, 'spirit/topic/private/delete.html', context)


@login_required
def join_in(request, topic_id):
    # This is for topic creators who left their own topics and want to join again
    topic = get_object_or_404(Topic, pk=topic_id, user=request.user, category_id=settings.ST_TOPIC_PRIVATE_CATEGORY_PK)

    if request.method == 'POST':
        form = TopicPrivateJoinForm(topic=topic, user=request.user, data=request.POST)

        if form.is_valid():
            topic_private_access_pre_create.send(sender=TopicPrivate, topic=topic, user=request.user)
            form.save()

            return redirect(request.POST.get('next', topic.get_absolute_url()))
    else:
        form = TopicPrivateJoinForm()

    context = {
        'topic': topic,
        'form': form
    }

    return render(request, 'spirit/topic/private/join.html', context)


@login_required
def index(request):
    topics = Topic.objects\
        .with_bookmarks(user=request.user)\
        .filter(topics_private__user=request.user)

    topics = yt_paginate(
        topics,
        per_page=config.topics_per_page,
        page_number=request.GET.get('page', 1)
    )

    context = {'topics': topics, }

    return render(request, 'spirit/topic/private/list.html', context)


@login_required
def index_author(request):
    # Show created topics but exclude those the user is participating on
    # TODO: show all, show join link in those the user is not participating
    # TODO: move to manager
    topics = Topic.objects\
        .filter(user=request.user, category_id=settings.ST_TOPIC_PRIVATE_CATEGORY_PK)\
        .exclude(topics_private__user=request.user)

    topics = yt_paginate(
        topics,
        per_page=config.topics_per_page,
        page_number=request.GET.get('page', 1)
    )

    context = {'topics': topics, }

    return render(request, 'spirit/topic/private/created_list.html', context)
