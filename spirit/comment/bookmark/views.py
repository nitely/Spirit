# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.http import Http404

from spirit.core.utils import json_response
from spirit.core.utils.views import is_ajax
from spirit.topic.models import Topic
from .forms import BookmarkForm


@require_POST
@login_required
def create(request, topic_id):
    if not is_ajax(request):
        return Http404()

    topic = get_object_or_404(Topic, pk=topic_id)
    form = BookmarkForm(
        user=request.user, topic=topic, data=request.POST)

    if form.is_valid():
        form.save()
        return json_response()

    return Http404()  # TODO: return errors (in json format)


@login_required
def find(request, topic_id):
    # TODO: test!, this aint used yet.
    bookmark = BookmarkForm.objects.filter(
        user=request.user, topic_id=topic_id)

    if not bookmark:
        topic = get_object_or_404(Topic, pk=topic_id)
        return redirect(topic.get_absolute_url())

    return redirect(bookmark.get_absolute_url())
