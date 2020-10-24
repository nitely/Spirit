# -*- coding: utf-8 -*-

import os
from datetime import timedelta

from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from spirit.core.conf import settings
from spirit.core.utils.models import AutoSlugField
from spirit.core.storage import spirit_storage_or_none, spirit_storage


def avatar_path(instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    return os.path.join(
        'spirit', 'avatars', str(instance.user_id), 'pic' + ext)


class UserProfile(models.Model):
    class Notify:
        (NEVER,
         IMMEDIATELY,
         WEEKLY,
         MENTION,
         REPLY) = (1 << x for x in range(5))
        WHEN = (
            (NEVER, _("Never")),
            (IMMEDIATELY, _("Immediately")),
            (WEEKLY, _("Weekly")))
        WHEN_VALUES = tuple(x for x, _ in WHEN)

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name=_("profile"),
        related_name='st',
        on_delete=models.CASCADE)

    slug = AutoSlugField(populate_from="user.username", db_index=False, blank=True)
    nickname = models.CharField(_("nickname"), max_length=255)
    location = models.CharField(_("location"), max_length=75, blank=True)
    last_seen = models.DateTimeField(_("last seen"), auto_now=True)
    last_ip = models.GenericIPAddressField(_("last ip"), blank=True, null=True)
    timezone = models.CharField(_("time zone"), max_length=32, default='UTC')
    avatar = models.ImageField(
        _("avatar"), upload_to=avatar_path, storage=spirit_storage_or_none,
        max_length=255, blank=True)
    notify = models.PositiveIntegerField(
        default=Notify.NEVER | Notify.MENTION | Notify.REPLY)
    is_administrator = models.BooleanField(_('administrator status'), default=False)
    is_moderator = models.BooleanField(_('moderator status'), default=False)
    is_verified = models.BooleanField(
        _('verified'), default=False,
        help_text=_(
            'Designates whether the user has verified his '
            'account by email or by other means. Un-select this '
            'to let the user activate his account.'))

    topic_count = models.PositiveIntegerField(_("topic count"), default=0)
    comment_count = models.PositiveIntegerField(_("comment count"), default=0)

    last_post_hash = models.CharField(_("last post hash"), max_length=32, blank=True)
    last_post_on = models.DateTimeField(_("last post on"), null=True, blank=True)

    class Meta:
        verbose_name = _("forum profile")
        verbose_name_plural = _("forum profiles")

    def save(self, *args, **kwargs):
        if self.user.is_superuser:
            self.is_administrator = True

        if self.is_administrator:
            self.is_moderator = True

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse(
            'spirit:user:detail',
            kwargs={'pk': self.user.pk, 'slug': self.slug})

    @property
    def notify_when(self):
        for c in self.Notify.WHEN_VALUES:
            if self.notify & c:
                return self.notify & c
        return self.Notify.NEVER

    def update_post_hash(self, post_hash):
        # Let the DB do the hash
        # comparison for atomicity
        return bool(
            UserProfile.objects
            .filter(pk=self.pk)
            .exclude(
                last_post_hash=post_hash,
                last_post_on__gte=timezone.now() - timedelta(
                    minutes=settings.ST_DOUBLE_POST_THRESHOLD_MINUTES))
            .update(
                last_post_hash=post_hash,
                last_post_on=timezone.now()))

    def small_avatar_name(self):
        assert self.avatar
        name, ext = os.path.splitext(self.avatar.name)
        return ''.join((name, '_small', ext))

    def small_avatar_url(self):
        return spirit_storage.url(self.small_avatar_name())
