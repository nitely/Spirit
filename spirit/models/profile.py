# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.core.urlresolvers import reverse
from django.utils.encoding import smart_text
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from spirit.utils.timezone import TIMEZONE_CHOICES


PROFILE_FIELDS = (
    'location', 'last_seen', 'last_ip', 'timezone', 'is_administrator',
    'is_moderator', 'topic_count', 'comment_count'
)


class ForumProfile(models.Model):

    location = models.CharField(_("location"), max_length=75, blank=True)
    last_seen = models.DateTimeField(_("last seen"), auto_now=True)
    last_ip = models.GenericIPAddressField(_("last ip"), blank=True, null=True)
    timezone = models.CharField(_("time zone"), max_length=32, choices=TIMEZONE_CHOICES, default='UTC')
    is_administrator = models.BooleanField(_('administrator status'), default=False)
    is_moderator = models.BooleanField(_('moderator status'), default=False)
    # is_verified = models.BooleanField(_('verified'), default=False)

    topic_count = models.PositiveIntegerField(_("topic count"), default=0)
    comment_count = models.PositiveIntegerField(_("comment count"), default=0)

    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='forum_profile')

    class Meta:
        verbose_name = _("forum profile")
        verbose_name_plural = _("forum profiles")

    def __unicode__(self):
        return self.slug

    def get_absolute_url(self):
        return reverse(
            'spirit:profile-detail',
            kwargs={'pk': self.user.pk, 'slug': self.slug}
        )

    @property
    def slug(self):
        if self.user:
            return slugify(smart_text(self.user.username))[:50].strip('-')

        return ''

    def save(self, *args, **kwargs):
        if self.user.is_superuser:
            self.is_administrator = True

        if self.is_administrator:
            self.is_moderator = True

        super(ForumProfile, self).save(*args, **kwargs)
