# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.contrib import messages

from spirit import utils
from .models import TopicFavorite
from .forms import FavoriteForm
from ..models import Topic


@require_POST
@login_required
def create(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)
    form = FavoriteForm(user=request.user, topic=topic, data=request.POST)

    if form.is_valid():
        form.save()
    else:
        messages.error(request, utils.render_form_errors(form))

    return redirect(request.POST.get('next', topic.get_absolute_url()))


@require_POST
@login_required
def delete(request, pk):
    favorite = get_object_or_404(TopicFavorite, pk=pk, user=request.user)
    favorite.delete()
    return redirect(request.POST.get('next', favorite.topic.get_absolute_url()))
