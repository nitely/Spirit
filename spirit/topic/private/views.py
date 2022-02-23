# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import HttpResponsePermanentRedirect

from djconfig import config

from spirit.core.conf import settings
from spirit.core import utils
from spirit.core.utils.http import safe_redirect
from spirit.core.utils.views import is_post, post_data
from spirit.core.utils.paginator import paginate, yt_paginate
from spirit.core.utils.ratelimit.decorators import ratelimit
from spirit.comment.forms import CommentForm
from spirit.comment.utils import comment_posted
from spirit.comment.models import Comment
from ..models import Topic
from ..utils import topic_viewed
from .utils import notify_access
from .models import TopicPrivate
from .forms import (
    TopicPrivateManyForm, TopicForPrivateForm,
    TopicPrivateJoinForm, TopicPrivateInviteForm)
from ..notification.models import TopicNotification

User = get_user_model()


@login_required
@ratelimit(rate='1/10s')
def publish(request, user_id=None):
    initial = None
    if user_id:  # todo: move to form
        user_to = get_object_or_404(User, pk=user_id)
        initial = {'users': [user_to.st.nickname]}

    user = request.user
    tform = TopicForPrivateForm(
        user=user, data=post_data(request))
    cform = CommentForm(
        user=user, data=post_data(request))
    tpform = TopicPrivateManyForm(
        user=user, data=post_data(request), initial=initial)

    if (is_post(request) and
            all([tform.is_valid(), cform.is_valid(), tpform.is_valid()]) and
            not request.is_limited()):
        if not user.st.update_post_hash(tform.get_topic_hash()):
            return safe_redirect(
                request, 'next', lambda: tform.category.get_absolute_url(), method='POST')

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

    return render(
        request=request,
        template_name='spirit/topic/private/publish.html',
        context={
            'tform': tform,
            'cform': cform,
            'tpform': tpform})


@login_required
def detail(request, topic_id, slug):
    topic_private = get_object_or_404(
        TopicPrivate.objects.select_related('topic'),
        topic_id=topic_id,
        user=request.user)
    topic = topic_private.topic

    if topic.slug != slug:
        return HttpResponsePermanentRedirect(topic.get_absolute_url())

    topic_viewed(request=request, topic=topic)

    comments = (
        Comment.objects
        .for_topic(topic=topic)
        .with_likes(user=request.user)
        .with_polls(user=request.user)
        .order_by('date'))

    comments = paginate(
        comments,
        per_page=config.comments_per_page,
        page_number=request.GET.get('page', 1)
    )

    return render(
        request=request,
        template_name='spirit/topic/private/detail.html',
        context={
            'topic': topic,
            'topic_private': topic_private,
            'comments': comments,})


@login_required
@require_POST
def create_access(request, topic_id):
    topic_private = TopicPrivate.objects.for_create_or_404(topic_id, request.user)
    form = TopicPrivateInviteForm(
        topic=topic_private.topic,
        data=post_data(request))

    if form.is_valid():
        form.save()
        notify_access(user=form.get_user(), topic_private=topic_private)
    else:
        messages.error(request, utils.render_form_errors(form))

    return safe_redirect(
        request, 'next', topic_private.get_absolute_url(), method='POST')


@login_required
def delete_access(request, pk):
    topic_private = TopicPrivate.objects.for_delete_or_404(pk, request.user)

    if request.method == 'POST':
        topic_private.delete()

        if request.user.pk == topic_private.user_id:
            return redirect(reverse("spirit:topic:private:index"))

        return safe_redirect(
            request, 'next', topic_private.get_absolute_url(), method='POST')

    return render(
        request=request,
        template_name='spirit/topic/private/delete.html',
        context={'topic_private': topic_private})


@login_required
def join_in(request, topic_id):
    # todo: replace by create_access()?
    # This is for topic creators who left their own topics and want to join again
    topic = get_object_or_404(
        Topic,
        pk=topic_id,
        user=request.user,
        category_id=settings.ST_TOPIC_PRIVATE_CATEGORY_PK)
    form = TopicPrivateJoinForm(
        topic=topic,
        user=request.user,
        data=post_data(request))
    if is_post(request) and form.is_valid():
        topic_private = form.save()
        notify_access(user=form.get_user(), topic_private=topic_private)
        return safe_redirect(
            request, 'next', topic.get_absolute_url(), method='POST')
    return render(
        request=request,
        template_name='spirit/topic/private/join.html',
        context={
            'topic': topic,
            'form': form})


@login_required
def index(request):
    topics = (
        Topic.objects
        .with_bookmarks(user=request.user)
        .filter(topics_private__user=request.user))
    topics = yt_paginate(
        topics,
        per_page=config.topics_per_page,
        page_number=request.GET.get('page', 1)
    )
    return render(
        request=request,
        template_name='spirit/topic/private/index.html',
        context={'topics': topics})


@login_required
def index_author(request):
    # Show created topics but exclude those the user is participating on
    # TODO: show all, show join link in those the user is not participating
    # TODO: move to manager
    topics = (
        Topic.objects
        .filter(
            user=request.user,
            category_id=settings.ST_TOPIC_PRIVATE_CATEGORY_PK)
        .exclude(topics_private__user=request.user))
    topics = yt_paginate(
        topics,
        per_page=config.topics_per_page,
        page_number=request.GET.get('page', 1)
    )
    return render(
        request=request,
        template_name='spirit/topic/private/index_author.html',
        context={'topics': topics})
