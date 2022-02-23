# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages

from .models import TopicFavorite
from .forms import FavoriteForm
from ..models import Topic
from spirit.core import utils
from spirit.core.utils.http import safe_redirect


@require_POST
@login_required
def create(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)
    form = FavoriteForm(user=request.user, topic=topic, data=request.POST)

    if form.is_valid():
        form.save()
    else:
        messages.error(request, utils.render_form_errors(form))

    return safe_redirect(request, 'next', topic.get_absolute_url(), method='POST')


@require_POST
@login_required
def delete(request, pk):
    favorite = get_object_or_404(TopicFavorite, pk=pk, user=request.user)
    favorite.delete()
    return safe_redirect(request, 'next', favorite.topic.get_absolute_url(), method='POST')
