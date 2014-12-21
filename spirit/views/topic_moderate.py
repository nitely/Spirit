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

    actions = None  # (do_action, undo_action)

    def update(self, request, pk, value, not_value):
        raise NotImplementedError()

    def send_signal(self, user, action):
        topic_post_moderate.send(sender=self.topic.__class__, user=user,
                                 topic=self.topic, action=action)

    def post(self, request, *args, **kwargs):
        pk = kwargs['pk']
        value = kwargs['value']
        not_value = not value
        count = self.update(request, pk, value, not_value)

        if count and self.actions is not None:
            action = self.actions[0] if value else self.actions[1]
            self.send_signal(request.user, action)

        return redirect(request.POST.get('next', self.topic.get_absolute_url()))

    def get(self, request, *args, **kwargs):
        return render(request, 'spirit/topic/topic_moderate.html', {'topic': self.topic, })

    @method_decorator(moderator_required)
    def dispatch(self, *args, **kwargs):
        self.topic = get_object_or_404(Topic, pk=kwargs['pk'])
        return super(TopicModerateBase, self).dispatch(*args, **kwargs)


class TopicModerateDelete(TopicModerateBase):

    def update(self, request, pk, value, not_value):
        return Topic.objects.filter(pk=pk, is_removed=not_value)\
            .update(is_removed=value)


class TopicModerateLock(TopicModerateBase):

    actions = (CLOSED, UNCLOSED)

    def update(self, request, pk, value, not_value):
        return Topic.objects.filter(pk=pk, is_closed=not_value)\
            .update(is_closed=value)


class TopicModeratePin(TopicModerateBase):

    actions = (PINNED, UNPINNED)

    def update(self, request, pk, value, not_value):
        return Topic.objects.filter(pk=pk, is_pinned=not_value)\
            .update(is_pinned=value)


class TopicModerateGlobalPin(TopicModerateBase):

    actions = (PINNED, UNPINNED)

    def update(self, request, pk, value, not_value):
        return Topic.objects.filter(pk=pk, is_globally_pinned=not_value)\
            .update(is_globally_pinned=value)
