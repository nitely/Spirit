# -*- coding: utf-8 -*-

import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import Http404, HttpResponse
from django.contrib import messages
from django.utils.html import escape
from django.urls import reverse

from djconfig import config
from infinite_scroll_pagination.serializers import to_page_key

from spirit.core.conf import settings
from spirit.core import utils
from spirit.core.utils.paginator import yt_paginate
from spirit.core.utils.paginator.infinite_paginator import paginate
from spirit.core.utils.views import is_ajax
from spirit.core.utils.http import safe_redirect
from spirit.topic.models import Topic
from .models import TopicNotification
from .forms import NotificationForm, NotificationCreationForm


@require_POST
@login_required
def create(request, topic_id):
    topic = get_object_or_404(
        Topic.objects.for_access(request.user),
        pk=topic_id)
    form = NotificationCreationForm(
        user=request.user,
        topic=topic,
        data=request.POST)

    if form.is_valid():
        form.save()
    else:
        messages.error(request, utils.render_form_errors(form))

    return safe_redirect(request, 'next', topic.get_absolute_url(), method='POST')


@require_POST
@login_required
def update(request, pk):
    notification = get_object_or_404(TopicNotification, pk=pk, user=request.user)
    form = NotificationForm(data=request.POST, instance=notification)

    if form.is_valid():
        form.save()
    else:
        messages.error(request, utils.render_form_errors(form))

    return safe_redirect(
        request, 'next', notification.topic.get_absolute_url(), method='POST')


@login_required
def index_ajax(request):
    if not is_ajax(request):
        return Http404()

    notifications = (
        TopicNotification.objects
            .for_access(request.user)
            .order_by("is_read", "-date")
            .with_related_data())
    notifications = notifications[:settings.ST_NOTIFICATIONS_PER_PAGE]
    notifications = [
        {'user': escape(n.comment.user.st.nickname),
         'action': n.action,
         'title': escape(n.topic.title),
         'url': n.get_absolute_url(),
         'is_read': n.is_read}
        for n in notifications]

    return HttpResponse(
        json.dumps({'n': notifications}),
        content_type="application/json")


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
        page_var='p',
        per_page=settings.ST_NOTIFICATIONS_PER_PAGE)
    return render(
        request=request,
        template_name='spirit/topic/notification/index_unread.html',
        context={
            'page': page,
            'next_page': to_page_key(**page.next_page())})


@login_required
def index(request):
    notifications = yt_paginate(
        TopicNotification.objects
            .for_access(request.user)
            .with_related_data(),
        per_page=config.topics_per_page,
        page_number=request.GET.get('page', 1))

    return render(
        request=request,
        template_name='spirit/topic/notification/index.html',
        context={'notifications': notifications})


@require_POST
@login_required
def mark_all_as_read(request):
    (TopicNotification.objects
        .for_access(request.user)
        .filter(is_read=False)
        .update(is_read=True))
    return safe_redirect(
        request, 'next', reverse('spirit:topic:notification:index'), method='POST')
