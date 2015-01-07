# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.utils.encoding import python_2_unicode_compatible


REASON_CHOICES = (
    (0, _("Spam")),
    (1, _("Other")),
)


@python_2_unicode_compatible
class CommentFlag(models.Model):

    moderator = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True)
    comment = models.OneToOneField('spirit.Comment')

    date = models.DateTimeField(auto_now_add=True)
    is_closed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date', '-pk']
        verbose_name = _("comment flag")
        verbose_name_plural = _("comments flags")

    def __str__(self):
        return "%s flagged" % self.comment

    # def get_absolute_url(self):
        # pass


@python_2_unicode_compatible
class Flag(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    comment = models.ForeignKey('spirit.Comment')

    date = models.DateTimeField(auto_now_add=True)
    reason = models.IntegerField(_("reason"), choices=REASON_CHOICES)
    body = models.TextField(_("body"), blank=True)

    class Meta:
        unique_together = ('user', 'comment')
        ordering = ['-date', '-pk']
        verbose_name = _("flag")
        verbose_name_plural = _("flags")

    def __str__(self):
        return "%s flagged %s" % (self.user, self.comment)
