# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import HttpResponsePermanentRedirect

from djconfig import config

from ...core.conf import settings
from ...core import utils
from ...core.utils.paginator import paginate, yt_paginate
from ...core.utils.ratelimit.decorators import ratelimit
from ...comment.forms import CommentForm
from ...comment.utils import comment_posted
from ...comment.models import Comment
from ..models import Topic
from ..utils import topic_viewed
from .utils import notify_access
from .models import TopicPrivate
from .forms import TopicPrivateManyForm, TopicForPrivateForm,\
    TopicPrivateJoinForm, TopicPrivateInviteForm
from ..notification.models import TopicNotification

User = get_user_model()


@login_required
@ratelimit(rate='1/10s')
def publish(request, user_id=None):
    user = request.user

    if request.method == 'POST':
        tform = TopicForPrivateForm(user=user, data=request.POST)
        cform = CommentForm(user=user, data=request.POST)
        tpform = TopicPrivateManyForm(user=user, data=request.POST)

        if (all([tform.is_valid(), cform.is_valid(), tpform.is_valid()]) and
                not request.is_limited()):
            if not user.st.update_post_hash(tform.get_topic_hash()):
                return redirect(
                    request.POST.get('next', None) or
                    tform.category.get_absolute_url())

            # wrap in transaction.atomic?
            topic = tform.save()
            cform.topic = topic
            comment = cform.save()
            comment_posted(comment=comment, mentions=None)
            tpform.topic = topic
            tpform.save_m2m()
            TopicNotification.bulk_create(
                users=tpform.get_users(), comment=comment)
            return redirect(topic.get_absolute_url())
    else:
        tform = TopicForPrivateForm()
        cform = CommentForm()
        initial = None

        if user_id:  # todo: move to form
            user_to = get_object_or_404(User, pk=user_id)
            initial = {'users': [user_to.username]}

        tpform = TopicPrivateManyForm(initial=initial)

    context = {
        'tform': tform,
        'cform': cform,
        'tpform': tpform}

    return render(request, 'spirit/topic/private/publish.html', context)


@login_required
def detail(request, topic_id, slug):
    topic_private = get_object_or_404(TopicPrivate.objects.select_related('topic'),
                                      topic_id=topic_id,
                                      user=request.user)
    topic = topic_private.topic

    if topic.slug != slug:
        return HttpResponsePermanentRedirect(topic.get_absolute_url())

    topic_viewed(request=request, topic=topic)

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
        form.save()
        notify_access(user=form.get_user(), topic_private=topic_private)
    else:
        messages.error(request, utils.render_form_errors(form))

    return redirect(request.POST.get('next', topic_private.get_absolute_url()))


@login_required
def delete_access(request, pk):
    topic_private = TopicPrivate.objects.for_delete_or_404(pk, request.user)

    if request.method == 'POST':
        topic_private.delete()

        if request.user.pk == topic_private.user_id:
            return redirect(reverse("spirit:topic:private:index"))

        return redirect(request.POST.get('next', topic_private.get_absolute_url()))

    context = {'topic_private': topic_private, }

    return render(request, 'spirit/topic/private/delete.html', context)


@login_required
def join_in(request, topic_id):
    # todo: replace by create_access()?
    # This is for topic creators who left their own topics and want to join again
    topic = get_object_or_404(
        Topic,
        pk=topic_id,
        user=request.user,
        category_id=settings.ST_TOPIC_PRIVATE_CATEGORY_PK
    )

    if request.method == 'POST':
        form = TopicPrivateJoinForm(topic=topic, user=request.user, data=request.POST)

        if form.is_valid():
            topic_private = form.save()
            notify_access(user=form.get_user(), topic_private=topic_private)
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

    return render(request, 'spirit/topic/private/index.html', context)


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

    return render(request, 'spirit/topic/private/index_author.html', context)
