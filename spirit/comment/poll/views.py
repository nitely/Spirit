# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.utils import timezone
from django.core.exceptions import PermissionDenied

from djconfig import config

from ...core import utils
from ...core.utils.paginator import yt_paginate
from .models import CommentPoll, CommentPollChoice, CommentPollVote
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
    poll = get_object_or_404(
        CommentPoll.objects.unremoved(),
        pk=pk
    )

    if not request.user.is_authenticated:
        return redirect_to_login(next=poll.get_absolute_url())

    form = PollVoteManyForm(user=request.user, poll=poll, data=request.POST)

    if form.is_valid():
        CommentPollChoice.decrease_vote_count(poll=poll, voter=request.user)
        form.save_m2m()
        CommentPollChoice.increase_vote_count(poll=poll, voter=request.user)
        return redirect(request.POST.get('next', poll.get_absolute_url()))

    messages.error(request, utils.render_form_errors(form))
    return redirect(request.POST.get('next', poll.get_absolute_url()))


@login_required
def voters(request, pk):
    # TODO: check if user has access to this topic/poll
    choice = get_object_or_404(
        CommentPollChoice.objects
            .unremoved()
            .select_related('poll'),
        pk=pk
    )

    if not choice.poll.can_show_results:
        raise PermissionDenied

    choice_votes = CommentPollVote.objects\
        .unremoved()\
        .for_choice(choice=choice)\
        .select_related('voter__st')

    choice_votes = yt_paginate(
        choice_votes,
        per_page=config.topics_per_page,
        page_number=request.GET.get('page', 1)
    )

    context = {
        'choice': choice,
        'votes': choice_votes
    }

    return render(request, 'spirit/comment/poll/voters.html', context)
