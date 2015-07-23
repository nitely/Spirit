# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import IntegrityError, transaction

from ..private.signals import topic_private_access_pre_create
from .models import TopicNotification, COMMENT


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


topic_private_access_pre_create.connect(topic_private_access_pre_create_handler, dispatch_uid=__name__)