# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import Http404, HttpResponse
from django.contrib import messages
from django.utils.html import escape

from djconfig import config

from ...core.conf import settings
from ...core import utils
from ...core.utils.paginator import yt_paginate
from ...core.utils.paginator.infinite_paginator import paginate
from ...topic.models import Topic
from .models import TopicNotification
from .forms import NotificationForm, NotificationCreationForm


@require_POST
@login_required
def create(request, topic_id):
    topic = get_object_or_404(Topic.objects.for_access(request.user),
                              pk=topic_id)
    form = NotificationCreationForm(user=request.user, topic=topic, data=request.POST)

    if form.is_valid():
        form.save()
    else:
        messages.error(request, utils.render_form_errors(form))

    return redirect(request.POST.get('next', topic.get_absolute_url()))


@require_POST
@login_required
def update(request, pk):
    notification = get_object_or_404(TopicNotification, pk=pk, user=request.user)
    form = NotificationForm(data=request.POST, instance=notification)

    if form.is_valid():
        form.save()
    else:
        messages.error(request, utils.render_form_errors(form))

    return redirect(request.POST.get('next', notification.topic.get_absolute_url()))


@login_required
def index_ajax(request):
    if not request.is_ajax():
        return Http404()

    notifications = (
        TopicNotification.objects
            .for_access(request.user)
            .order_by("is_read", "-date")
            .with_related_data())

    notifications = notifications[:settings.ST_NOTIFICATIONS_PER_PAGE]

    notifications = [
        {
            'user': escape(n.comment.user.st.nickname),
            'action': n.action,
            'title': escape(n.topic.title),
            'url': n.get_absolute_url(),
            'is_read': n.is_read
        }
        for n in notifications
    ]

    return HttpResponse(json.dumps({'n': notifications}), content_type="application/json")


@login_required
def index_unread(request):
    notifications = (
        TopicNotification.objects
            .for_access(request.user)
            .filter(is_read=False)
            .with_related_data())

    page = paginate(
        request,
        query_set=notifications,
        lookup_field='date',
        page_var='notif',
        per_page=settings.ST_NOTIFICATIONS_PER_PAGE)

    next_page_pk = None
    if page:
        next_page_pk = page[-1].pk

    context = {
        'page': page,
        'next_page_pk': next_page_pk}

    return render(request, 'spirit/topic/notification/index_unread.html', context)


@login_required
def index(request):
    notifications = yt_paginate(
        TopicNotification.objects
            .for_access(request.user)
            .with_related_data(),
        per_page=config.topics_per_page,
        page_number=request.GET.get('page', 1))

    context = {'notifications': notifications}

    return render(request, 'spirit/topic/notification/index.html', context)
