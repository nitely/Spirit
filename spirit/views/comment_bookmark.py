#-*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.views.decorators.http import require_POST
from django.http import Http404

from spirit.utils import json_response
from spirit.models.topic import Topic
from spirit.models.comment_bookmark import CommentBookmark
from spirit.forms.comment_bookmark import BookmarkForm


@require_POST
@login_required
def bookmark_create(request, topic_id):
    if not request.is_ajax():
        return Http404()

    topic = get_object_or_404(Topic, pk=topic_id)
    form = BookmarkForm(data=request.POST)

    if not form.is_valid():
        return Http404()

    comment_number = form.cleaned_data['comment_number']

    # Bookmark is created/updated on topic view.
    CommentBookmark.objects.filter(user=request.user, topic=topic)\
        .update(comment_number=comment_number)

    return json_response()


@login_required
def bookmark_find(request, topic_id):
    # TODO: test!, this aint used yet.
    bookmark = BookmarkForm.objects.filter(user=request.user, topic_id=topic_id)

    if not bookmark:
        topic = get_object_or_404(Topic, pk=topic_id)
        return redirect(topic.get_absolute_url())

    return redirect(bookmark.get_absolute_url())