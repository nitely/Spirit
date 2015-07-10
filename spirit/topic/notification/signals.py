# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.utils import timezone
from django.db import IntegrityError, transaction

from ...comment.signals import comment_posted
from ..private.signals import topic_private_post_create, topic_private_access_pre_create
from ..signals import topic_viewed
from .models import TopicNotification, COMMENT, MENTION


def notification_comment_posted_handler(sender, comment, **kwargs):
    # Create Notification for poster
    # if not exists create a dummy one with defaults
    try:
        TopicNotification.objects.get_or_create(user=comment.user, topic=comment.topic,
                                                defaults={'action': COMMENT,
                                                          'is_read': True,
                                                          'is_active': True})
    except IntegrityError:
        pass

    TopicNotification.objects.filter(topic=comment.topic, is_active=True, is_read=True)\
        .exclude(user=comment.user)\
        .update(comment=comment, is_read=False, action=COMMENT, date=timezone.now())


def mention_comment_posted_handler(sender, comment, mentions, **kwargs):
    if not mentions:
        return

    for username, user in mentions.items():
        try:
            with transaction.atomic():
                TopicNotification.objects.create(user=user, topic=comment.topic,
                                                 comment=comment, action=MENTION)
        except IntegrityError:
            pass

    TopicNotification.objects.filter(user__in=mentions.values(), topic=comment.topic, is_read=True)\
        .update(comment=comment, is_read=False, action=MENTION, date=timezone.now())


def comment_posted_handler(sender, comment, mentions, **kwargs):
    notification_comment_posted_handler(sender, comment, **kwargs)
    mention_comment_posted_handler(sender, comment, mentions, **kwargs)


def topic_private_post_create_handler(sender, topics_private, comment, **kwargs):
    # topic.user notification is created on comment_posted
    TopicNotification.objects.bulk_create([TopicNotification(user=tp.user, topic=tp.topic,
                                                             comment=comment, action=COMMENT,
                                                             is_active=True)
                                           for tp in topics_private
                                           if tp.user != tp.topic.user])


def topic_private_access_pre_create_handler(sender, topic, user, **kwargs):
    # TODO: use update_or_create on django 1.7
    # change to post create
    try:
        with transaction.atomic():
            TopicNotification.objects.create(user=user, topic=topic,
                                             comment=topic.comment_set.last(), action=COMMENT,
                                             is_active=True)
    except IntegrityError:
        pass


def topic_viewed_handler(sender, request, topic, **kwargs):
    if not request.user.is_authenticated():
        return

    TopicNotification.objects.filter(user=request.user, topic=topic)\
        .update(is_read=True)


comment_posted.connect(comment_posted_handler, dispatch_uid=__name__)
topic_private_post_create.connect(topic_private_post_create_handler, dispatch_uid=__name__)
topic_private_access_pre_create.connect(topic_private_access_pre_create_handler, dispatch_uid=__name__)
topic_viewed.connect(topic_viewed_handler, dispatch_uid=__name__)
