# -*- coding: utf-8 -*-

from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404

from ...core.utils.views import is_post
from ...core.utils.decorators import moderator_required
from ...comment.models import Comment
from ..models import Topic


@moderator_required
def _moderate(request, pk, field_name, to_value, action=None):
    topic = get_object_or_404(Topic, pk=pk)

    if is_post(request):
        count = (
            Topic.objects
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

    return render(
        request=request,
        template_name='spirit/topic/moderate.html',
        context={'topic': topic})


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
        action=Comment.CLOSED)


def unlock(request, pk):
    return _moderate(
        request=request,
        pk=pk,
        field_name='is_closed',
        to_value=False,
        action=Comment.UNCLOSED)


def pin(request, pk):
    return _moderate(
        request=request,
        pk=pk,
        field_name='is_pinned',
        to_value=True,
        action=Comment.PINNED)


def unpin(request, pk):
    return _moderate(
        request=request,
        pk=pk,
        field_name='is_pinned',
        to_value=False,
        action=Comment.UNPINNED)


def global_pin(request, pk):
    return _moderate(
        request=request,
        pk=pk,
        field_name='is_globally_pinned',
        to_value=True,
        action=Comment.PINNED)


def global_unpin(request, pk):
    return _moderate(
        request=request,
        pk=pk,
        field_name='is_globally_pinned',
        to_value=False,
        action=Comment.UNPINNED)
