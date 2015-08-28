# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.utils import timezone

from .managers import CommentPollQuerySet, CommentPollChoiceQuerySet, CommentPollVoteQuerySet


class CommentPoll(models.Model):

    comment = models.ForeignKey('spirit_comment.Comment', related_name='comment_polls')

    name = models.CharField(_("name"), max_length=255)
    title = models.CharField(_("title"), max_length=255)
    choice_limit = models.PositiveIntegerField(_("choice limit"), default=1)
    is_closed = models.BooleanField(default=False)
    is_removed = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    objects = CommentPollQuerySet.as_manager()

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

    @classmethod
    def update_or_create_many(cls, comment, polls_raw):
        cls.objects \
            .for_comment(comment) \
            .update(is_removed=True)

        for poll in polls_raw:
            cls.objects.update_or_create(
                comment=comment,
                name=poll['name'],
                defaults={'is_removed': False}
            )


class CommentPollChoice(models.Model):

    poll = models.ForeignKey(CommentPoll, verbose_name=_("poll"), related_name='poll_choices')

    number = models.PositiveIntegerField(_("number"))
    description = models.CharField(_("choice description"), max_length=255)
    vote_count = models.PositiveIntegerField(_("vote count"), default=0)
    is_removed = models.BooleanField(default=False)

    objects = CommentPollChoiceQuerySet.as_manager()

    class Meta:
        unique_together = ('poll', 'number')
        ordering = ['-pk', ]
        verbose_name = _("poll choice")
        verbose_name_plural = _("poll choices")

    @property
    def vote(self):
        # *votes* is dynamically created by comments.with_polls()
        try:
            assert len(self.votes) <= 1, "Panic, too many votes"
            return self.votes[0]
        except (AttributeError, IndexError):
            return

    @classmethod
    def update_or_create_many(cls, comment, choices_raw):
        cls.objects \
            .for_comment(comment) \
            .update(is_removed=True)

        poll_ids_by_name = dict(
            CommentPoll.objects
                .for_comment(comment)
                .values_list('name', 'id')
        )

        for choice in choices_raw:
            cls.objects.update_or_create(
                poll_id=poll_ids_by_name[choice['poll_name']],
                number=choice['number'],
                defaults={
                    'description': choice['description'],
                    'is_removed': False
                }
            )


class CommentPollVote(models.Model):

    choice = models.ForeignKey(CommentPollChoice, verbose_name=_("poll choice"), related_name='choice_votes')
    voter = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("voter"))

    is_removed = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    objects = CommentPollVoteQuerySet.as_manager()

    class Meta:
        unique_together = ('voter', 'choice')
        ordering = ['-created_at', '-pk', ]
        verbose_name = _("poll vote")
        verbose_name_plural = _("poll votes")
