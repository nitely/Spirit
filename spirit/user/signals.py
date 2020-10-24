# -*- coding: utf-8 -*-

from django.db.models.signals import post_save
from django.contrib.auth import get_user_model

from spirit.core.conf import settings
from .models import UserProfile

User = get_user_model()
Notify = UserProfile.Notify
NOTIFY = {
    'never': Notify.NEVER,
    'immediately': Notify.IMMEDIATELY,
    'weekly': Notify.WEEKLY}


def update_or_create_user_profile(sender, instance, created, **kwargs):
    user = instance
    if created:
        UserProfile.objects.create(
            user=user,
            nickname=user.username,
            notify=NOTIFY[settings.ST_NOTIFY_WHEN] | Notify.MENTION | Notify.REPLY)
    else:
        user.st.save()


def lower_username(sender, instance, created, **kwargs):
    user = instance
    if created and settings.ST_CASE_INSENSITIVE_USERNAMES:
        (User.objects
         .filter(pk=user.pk)
         .update(username=user.username.lower()))
        user.username = user.username.lower()


def post_save_receivers(*args, **kwargs):
    update_or_create_user_profile(*args, **kwargs)
    lower_username(*args, **kwargs)


post_save.connect(post_save_receivers, sender=User, dispatch_uid=__name__)
