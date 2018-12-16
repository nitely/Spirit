# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.shortcuts import get_object_or_404
from django.db.models import Q, Prefetch

from .like.models import CommentLike
from .poll.models import CommentPoll, CommentPollChoice, CommentPollVote


class CommentQuerySet(models.QuerySet):

    def filter(self, *args, **kwargs):
        return (
            super(CommentQuerySet, self)
            .filter(*args, **kwargs)
            .select_related('user__st'))

    def unremoved(self):
        # TODO: remove action
        return self.filter(
            Q(topic__category__parent=None) |
            Q(topic__category__parent__is_removed=False),
            topic__category__is_removed=False,
            topic__is_removed=False,
            is_removed=False,
            action=0)

    def public(self):
        return self.filter(topic__category__is_private=False)

    def visible(self):
        return self.unremoved().public()

    def for_topic(self, topic):
        return self.filter(topic=topic)

    def _access(self, user):
        return self.filter(
            Q(topic__category__is_private=False) |
            Q(topic__topics_private__user=user))

    def with_likes(self, user):
        if not user.is_authenticated:
            return self

        user_likes = CommentLike.objects.filter(user=user)
        prefetch = Prefetch(
            "comment_likes",
            queryset=user_likes,
            to_attr='likes')
        return self.prefetch_related(prefetch)

    def with_polls(self, user):
        visible_polls = CommentPoll.objects.unremoved()
        prefetch_polls = Prefetch(
            "comment_polls",
            queryset=visible_polls,
            to_attr='polls')

        # Choices are attached to polls
        visible_choices = CommentPollChoice.objects.unremoved()
        prefetch_choices = Prefetch(
            "polls__poll_choices",
            queryset=visible_choices,
            to_attr='choices')

        if not user.is_authenticated:
            return self.prefetch_related(prefetch_polls, prefetch_choices)

        # Votes are attached to choices
        visible_votes = (
            CommentPollVote.objects
            .unremoved()
            .for_voter(user))
        prefetch_votes = Prefetch(
            "polls__choices__choice_votes",
            queryset=visible_votes,
            to_attr='votes')

        return self.prefetch_related(prefetch_polls, prefetch_choices, prefetch_votes)

    def for_access(self, user):
        return self.unremoved()._access(user=user)

    def for_update_or_404(self, pk, user):
        if user.st.is_moderator:
            return get_object_or_404(self._access(user=user), pk=pk)
        return get_object_or_404(self.for_access(user), user=user, pk=pk)
