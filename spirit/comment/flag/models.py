# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.utils import timezone


REASON_CHOICES = (
    (0, _("Spam")),
    (1, _("Other")),
)


class CommentFlag(models.Model):

    moderator = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True)
    comment = models.OneToOneField('spirit_comment.Comment')

    date = models.DateTimeField(default=timezone.now)
    is_closed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date', '-pk']
        verbose_name = _("comment flag")
        verbose_name_plural = _("comments flags")

    # def get_absolute_url(self):
        # pass


class Flag(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    comment = models.ForeignKey('spirit_comment.Comment')

    date = models.DateTimeField(default=timezone.now)
    reason = models.IntegerField(_("reason"), choices=REASON_CHOICES)
    body = models.TextField(_("body"), blank=True)

    class Meta:
        unique_together = ('user', 'comment')
        ordering = ['-date', '-pk']
        verbose_name = _("flag")
        verbose_name_plural = _("flags")
