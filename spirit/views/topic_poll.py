#-*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse

from spirit.models.topic_poll import TopicPoll
from spirit.forms.topic_poll import TopicPollChoiceFormSet, TopicPollForm


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