#-*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.conf import settings

from spirit import utils

from spirit.models.topic_poll import TopicPoll
from spirit.forms.topic_poll import TopicPollChoiceFormSet, TopicPollForm, TopicPollVoteManyForm


@login_required
def poll_update(request, pk):
    poll = get_object_or_404(TopicPoll, pk=pk, topic__user=request.user)

    if request.method == 'POST':
        form = TopicPollForm(data=request.POST, instance=poll)
        formset = TopicPollChoiceFormSet(data=request.POST, instance=poll)

        if form.is_valid() and formset.is_valid():
            poll = form.save()
            choices = formset.save()
            return redirect(request.POST.get('next', poll.get_absolute_url()))
    else:
        form = TopicPollForm(instance=poll)
        formset = TopicPollChoiceFormSet(instance=poll)

    return render(request, 'spirit/topic_poll/poll_update.html', {'form': form, 'formset': formset})


@login_required
def poll_close(request, pk):
    poll = get_object_or_404(TopicPoll, pk=pk, topic__user=request.user)

    if request.method == 'POST':
        not_is_closed = not poll.is_closed
        TopicPoll.objects.filter(pk=poll.pk)\
            .update(is_closed=not_is_closed)

        return redirect(request.GET.get('next', poll.get_absolute_url()))

    return render(request, 'spirit/topic_poll/poll_close.html', {'poll': poll, })


@require_POST
def poll_vote(request, pk):
    poll = get_object_or_404(TopicPoll, pk=pk)

    if not request.user.is_authenticated():
        return redirect_to_login(next=poll.get_absolute_url(),
                                 login_url=settings.LOGIN_URL)

    form = TopicPollVoteManyForm(user=request.user, poll=poll, data=request.POST)

    if form.is_valid():
        form.save_m2m()
        return redirect(request.POST.get('next', poll.get_absolute_url()))
    else:
        messages.error(request, utils.render_form_errors(form))
        return redirect(request.POST.get('next', poll.get_absolute_url()))