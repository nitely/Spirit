# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from ...core.conf import settings

REASON_CHOICES = (
    (0, _("Spam")),
    (1, _("Other")))


class CommentFlag(models.Model):

    moderator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='st_comment_flags',
        null=True,
        blank=True,
        on_delete=models.CASCADE)
    comment = models.OneToOneField(
        'spirit_comment.Comment',
        on_delete=models.CASCADE)

    date = models.DateTimeField(default=timezone.now)
    is_closed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date', '-pk']
        verbose_name = _("comment flag")
        verbose_name_plural = _("comments flags")

    # def get_absolute_url(self):
        # pass


class Flag(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='st_flags',
        on_delete=models.CASCADE)
    comment = models.ForeignKey(
        'spirit_comment.Comment',
        on_delete=models.CASCADE)

    date = models.DateTimeField(default=timezone.now)
    reason = models.IntegerField(_("reason"), choices=REASON_CHOICES)
    body = models.TextField(_("body"), blank=True)

    class Meta:
        unique_together = ('user', 'comment')
        ordering = ['-date', '-pk']
        verbose_name = _("flag")
        verbose_name_plural = _("flags")
