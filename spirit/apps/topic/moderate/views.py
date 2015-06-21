# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.utils.decorators import method_decorator

from spirit.utils.decorators import moderator_required
from ...comment.models import CLOSED, UNCLOSED, PINNED, UNPINNED
from ..models import Topic
from .signals import topic_post_moderate


class BaseView(View):

    action = None
    field_name = None
    to_value = None  # bool

    def update(self, pk):
        not_value = not self.to_value
        return Topic.objects\
            .filter(**{'pk': pk, self.field_name: not_value})\
            .update(**{self.field_name: self.to_value, })

    def send_signal(self, user, action):
        topic_post_moderate.send(sender=self.topic.__class__, user=user,
                                 topic=self.topic, action=action)

    def post(self, request, *args, **kwargs):
        pk = kwargs['pk']
        count = self.update(pk)

        if count and self.action is not None:
            self.send_signal(request.user, self.action)

        return redirect(request.POST.get('next', self.topic.get_absolute_url()))

    def get(self, request, *args, **kwargs):
        return render(request, 'spirit/topic/moderate.html', {'topic': self.topic, })

    def check_configuration(self):
        assert self.field_name is not None, "You forgot to set field_name attribute"
        assert self.to_value is not None, "You forgot to set to_value attribute"

    @method_decorator(moderator_required)
    def dispatch(self, *args, **kwargs):
        self.check_configuration()
        self.topic = get_object_or_404(Topic, pk=kwargs['pk'])
        return super(BaseView, self).dispatch(*args, **kwargs)


class DeleteView(BaseView):

    field_name = 'is_removed'
    to_value = True


class UnDeleteView(BaseView):

    field_name = 'is_removed'
    to_value = False


class LockView(BaseView):

    action = CLOSED
    field_name = 'is_closed'
    to_value = True


class UnLockView(BaseView):

    action = UNCLOSED
    field_name = 'is_closed'
    to_value = False


class PinView(BaseView):

    action = PINNED
    field_name = 'is_pinned'
    to_value = True


class UnPinView(BaseView):

    action = UNPINNED
    field_name = 'is_pinned'
    to_value = False


class GlobalPinView(BaseView):

    action = PINNED
    field_name = 'is_globally_pinned'
    to_value = True


class GlobalUnPinView(BaseView):

    action = UNPINNED
    field_name = 'is_globally_pinned'
    to_value = False
