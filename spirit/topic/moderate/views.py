# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404

from ...core.utils.decorators import moderator_required
from ...comment.models import Comment, CLOSED, UNCLOSED, PINNED, UNPINNED
from ..models import Topic


@moderator_required
def _moderate(request, pk, field_name, to_value, action=None):
    topic = get_object_or_404(Topic, pk=pk)

    if request.method == 'POST':
        count = (Topic.objects
                 .filter(pk=pk)
                 .exclude(**{field_name: to_value})
                 .update(**{
                    field_name: to_value,
                    'reindex_at': timezone.now()}))

        if count and action is not None:
            Comment.create_moderation_action(
                user=request.user,
                topic=topic,
                action=action)

        return redirect(request.POST.get(
            'next', topic.get_absolute_url()))
    else:
        return render(
            request, 'spirit/topic/moderate.html', {'topic': topic})


def delete(request, pk):
    return _moderate(
        request=request,
        pk=pk,
        field_name='is_removed',
        to_value=True)


def undelete(request, pk):
    return _moderate(
        request=request,
        pk=pk,
        field_name='is_removed',
        to_value=False)


def lock(request, pk):
    return _moderate(
        request=request,
        pk=pk,
        field_name='is_closed',
        to_value=True,
        action=CLOSED)


def unlock(request, pk):
    return _moderate(
        request=request,
        pk=pk,
        field_name='is_closed',
        to_value=False,
        action=UNCLOSED)


def pin(request, pk):
    return _moderate(
        request=request,
        pk=pk,
        field_name='is_pinned',
        to_value=True,
        action=PINNED)


def unpin(request, pk):
    return _moderate(
        request=request,
        pk=pk,
        field_name='is_pinned',
        to_value=False,
        action=UNPINNED)


def global_pin(request, pk):
    return _moderate(
        request=request,
        pk=pk,
        field_name='is_globally_pinned',
        to_value=True,
        action=PINNED)


def global_unpin(request, pk):
    return _moderate(
        request=request,
        pk=pk,
        field_name='is_globally_pinned',
        to_value=False,
        action=UNPINNED)
