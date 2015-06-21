# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from spirit.templatetags.registry import register

from .models import TopicNotification
from .forms import NotificationForm


@register.assignment_tag()
def has_topic_notifications(user):
    return TopicNotification.objects.for_access(user=user).unread().exists()


@register.inclusion_tag('spirit/topic/notification/_form.html')
def render_notification_form(user, topic, next=None):
    # TODO: remove form and use notification_activate and notification_deactivate ?
    try:
        notification = TopicNotification.objects.get(user=user, topic=topic)
    except TopicNotification.DoesNotExist:
        notification = None

    initial = {}

    if notification:
        initial['is_active'] = not notification.is_active

    form = NotificationForm(initial=initial)
    return {'form': form, 'topic_id': topic.pk, 'notification': notification, 'next': next}
