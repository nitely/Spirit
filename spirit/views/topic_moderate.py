# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.utils.decorators import method_decorator

from spirit.utils.decorators import moderator_required
from spirit.models.comment import CLOSED, UNCLOSED, PINNED, UNPINNED

from spirit.models.topic import Topic
from spirit.signals.topic_moderate import topic_post_moderate


class TopicModerateBase(View):

    def update(self, request, pk, value, not_value):
        raise NotImplementedError()

    def post(self, request, *args, **kwargs):
        pk = kwargs['pk']
        value = kwargs['value']
        not_value = not value
        self.update(request, pk, value, not_value)
        return redirect(request.POST.get('next', self.topic.get_absolute_url()))

    def get(self, request, *args, **kwargs):
        return render(request, 'spirit/topic/topic_moderate.html', {'topic': self.topic, })

    @method_decorator(moderator_required)
    def dispatch(self, *args, **kwargs):
        self.topic = get_object_or_404(Topic, pk=kwargs['pk'])
        return super(TopicModerateBase, self).dispatch(*args, **kwargs)


class TopicModerateDelete(TopicModerateBase):

    def update(self, request, pk, value, not_value):
        Topic.objects.filter(pk=pk, is_removed=not_value)\
            .update(is_removed=value)


class TopicModerateLock(TopicModerateBase):

    def update(self, request, pk, value, not_value):
        count = Topic.objects.filter(pk=pk, is_closed=not_value)\
            .update(is_closed=value)

        if count:
            action = CLOSED if value else UNCLOSED
            topic_post_moderate.send(sender=self.topic.__class__, user=request.user,
                                     topic=self.topic, action=action)


class TopicModeratePin(TopicModerateBase):

    def update(self, request, pk, value, not_value):
        count = Topic.objects.filter(pk=pk, is_pinned=not_value)\
            .update(is_pinned=value)

        if count:
            action = PINNED if value else UNPINNED
            topic_post_moderate.send(sender=self.topic.__class__, user=request.user,
                                     topic=self.topic, action=action)
