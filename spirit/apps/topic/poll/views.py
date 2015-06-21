# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.conf import settings

from spirit import utils
from .models import TopicPoll
from .forms import TopicPollChoiceFormSet, TopicPollForm, TopicPollVoteManyForm
from .signals import topic_poll_pre_vote, topic_poll_post_vote


@login_required
def update(request, pk):
    poll = get_object_or_404(TopicPoll, pk=pk, topic__user=request.user)

    if request.method == 'POST':
        form = TopicPollForm(data=request.POST, instance=poll)
        formset = TopicPollChoiceFormSet(data=request.POST, instance=poll)

        if all([form.is_valid(), formset.is_valid()]):  # TODO: test!
            poll = form.save()
            formset.save()
            return redirect(request.POST.get('next', poll.get_absolute_url()))
    else:
        form = TopicPollForm(instance=poll)
        formset = TopicPollChoiceFormSet(instance=poll)

    context = {
        'form': form,
        'formset': formset
    }

    return render(request, 'spirit/topic/poll/update.html', context)


@login_required
def close(request, pk):
    poll = get_object_or_404(TopicPoll, pk=pk, topic__user=request.user)

    if request.method == 'POST':
        not_is_closed = not poll.is_closed
        TopicPoll.objects.filter(pk=poll.pk)\
            .update(is_closed=not_is_closed)

        return redirect(request.GET.get('next', poll.get_absolute_url()))

    context = {'poll': poll, }

    return render(request, 'spirit/topic/poll/close.html', context)


@require_POST
def vote(request, pk):
    # TODO: check if user has access to this topic/poll
    poll = get_object_or_404(TopicPoll, pk=pk)

    if not request.user.is_authenticated():
        return redirect_to_login(next=poll.get_absolute_url(),
                                 login_url=settings.LOGIN_URL)

    form = TopicPollVoteManyForm(user=request.user, poll=poll, data=request.POST)

    if form.is_valid():
        topic_poll_pre_vote.send(sender=poll.__class__, poll=poll, user=request.user)
        form.save_m2m()
        topic_poll_post_vote.send(sender=poll.__class__, poll=poll, user=request.user)
        return redirect(request.POST.get('next', poll.get_absolute_url()))

    messages.error(request, utils.render_form_errors(form))
    return redirect(request.POST.get('next', poll.get_absolute_url()))
