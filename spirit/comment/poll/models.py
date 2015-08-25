# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.utils import timezone


class CommentPoll(models.Model):

    comment = models.ForeignKey('spirit_comment.Comment', related_name='polls')

    name = models.CharField(_("name"), max_length=255)
    title = models.CharField(_("title"), max_length=255)
    choice_limit = models.PositiveIntegerField(_("choice limit"), default=1)
    is_closed = models.BooleanField(default=False)
    is_removed = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('comment', 'name')
        ordering = ['-pk', ]
        verbose_name = _("comment poll")
        verbose_name_plural = _("comments polls")

    def get_absolute_url(self):
        return self.comment.get_absolute_url()

    @property
    def is_multiple_choice(self):
        return self.choice_limit > 1


class CommentPollChoice(models.Model):

    poll = models.ForeignKey(CommentPoll, verbose_name=_("poll"), related_name='choices')

    number = models.PositiveIntegerField(_("number"))
    description = models.CharField(_("choice description"), max_length=255)
    vote_count = models.PositiveIntegerField(_("vote count"), default=0)
    is_removed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('poll', 'number')
        ordering = ['-pk', ]
        verbose_name = _("poll choice")
        verbose_name_plural = _("poll choices")


class CommentPollVote(models.Model):

    choice = models.ForeignKey(CommentPollChoice, verbose_name=_("poll choice"), related_name='votes')
    voter = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("voter"))

    is_removed = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('voter', 'choice')
        ordering = ['-created_at', '-pk', ]
        verbose_name = _("poll vote")
        verbose_name_plural = _("poll votes")
