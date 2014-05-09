#-*- coding: utf-8 -*-

from . import register

from spirit.models.topic_notification import TopicNotification
from spirit.forms.topic_notification import NotificationForm


@register.assignment_tag()
def has_topic_notifications(user):
    return TopicNotification.objects.for_access(user=user)\
        .filter(is_read=False)\
        .exists()


@register.inclusion_tag('spirit/topic_notification/_form.html')
def render_notification_form(user, topic, next=None):
    try:
        notification = TopicNotification.objects.get(user=user, topic=topic)
    except TopicNotification.DoesNotExist:
        notification = None

    initial = {}

    if notification:
        initial['is_active'] = not notification.is_active

    form = NotificationForm(initial=initial)
    return {'form': form, 'topic_id': topic.pk, 'notification': notification, 'next': next}