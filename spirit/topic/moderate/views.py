# -*- coding: utf-8 -*-

from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.translation import gettext as _

from spirit.core.utils.views import is_post
from spirit.core.utils.decorators import moderator_required
from spirit.comment.models import Comment
from spirit.topic.models import Topic


@moderator_required
def _moderate(request, pk, field_name, to_value, action=None, message=None):
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

        if message is not None:
            messages.info(request, message)

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
        to_value=True,
        message=_("The topic has been deleted"))


def undelete(request, pk):
    return _moderate(
        request=request,
        pk=pk,
        field_name='is_removed',
        to_value=False,
        message=_("The topic has been undeleted"))


def lock(request, pk):
    return _moderate(
        request=request,
        pk=pk,
        field_name='is_closed',
        to_value=True,
        action=Comment.CLOSED,
        message=_("The topic has been locked"))


def unlock(request, pk):
    return _moderate(
        request=request,
        pk=pk,
        field_name='is_closed',
        to_value=False,
        action=Comment.UNCLOSED,
        message=_("The topic has been unlocked"))


def pin(request, pk):
    return _moderate(
        request=request,
        pk=pk,
        field_name='is_pinned',
        to_value=True,
        action=Comment.PINNED,
        message=_("The topic has been pinned"))


def unpin(request, pk):
    return _moderate(
        request=request,
        pk=pk,
        field_name='is_pinned',
        to_value=False,
        action=Comment.UNPINNED,
        message=_("The topic has been unpinned"))


def global_pin(request, pk):
    return _moderate(
        request=request,
        pk=pk,
        field_name='is_globally_pinned',
        to_value=True,
        action=Comment.PINNED,
        message=_("The topic has been globally pinned"))


def global_unpin(request, pk):
    return _moderate(
        request=request,
        pk=pk,
        field_name='is_globally_pinned',
        to_value=False,
        action=Comment.UNPINNED,
        message=_("The topic has been globally unpinned"))
