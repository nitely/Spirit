# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.utils import timezone

from ...core import utils
from .models import CommentPoll
from .forms import PollVoteManyForm


@login_required
@require_POST
def close_or_open(request, pk, close=True):
    # todo: moderators should be able to close it
    poll = get_object_or_404(
        CommentPoll,
        pk=pk,
        comment__user=request.user
    )

    if close:
        close_at = timezone.now()
    else:
        close_at = None

    CommentPoll.objects\
        .filter(pk=poll.pk)\
        .update(close_at=close_at)

    return redirect(request.GET.get('next', poll.get_absolute_url()))


@require_POST
def vote(request, pk):
    # TODO: check if user has access to this topic/poll
    poll = get_object_or_404(CommentPoll, pk=pk)

    if not request.user.is_authenticated():
        return redirect_to_login(next=poll.get_absolute_url())

    form = PollVoteManyForm(user=request.user, poll=poll, data=request.POST)

    if form.is_valid():
        # topic_poll_pre_vote.send(sender=poll.__class__, poll=poll, user=request.user)
        form.save_m2m()
        # topic_poll_post_vote.send(sender=poll.__class__, poll=poll, user=request.user)
        return redirect(request.POST.get('next', poll.get_absolute_url()))

    messages.error(request, utils.render_form_errors(form))
    return redirect(request.POST.get('next', poll.get_absolute_url()))
