# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models


class CommentPollQuerySet(models.QuerySet):

    def unremoved(self):
        return self.filter(is_removed=False)

    def for_comment(self, comment):
        return self.filter(comment=comment)


class CommentPollChoiceQuerySet(models.QuerySet):

    def unremoved(self):
        return self.filter(is_removed=False)

    def for_comment(self, comment):
        return self.filter(poll__comment=comment)

    def for_poll(self, poll):
        return self.filter(poll=poll)

    def for_voter(self, voter):
        return self.filter(
            choice_votes__voter=voter,
            choice_votes__is_removed=False
        )

    def for_vote(self, poll, voter):
        return self \
            .for_poll(poll) \
            .for_voter(voter) \
            .unremoved()


class CommentPollVoteQuerySet(models.QuerySet):

    def unremoved(self):
        return self.filter(is_removed=False)

    def for_voter(self, user):
        return self.filter(voter=user)

    def for_choice(self, choice):
        return self.filter(choice=choice)
