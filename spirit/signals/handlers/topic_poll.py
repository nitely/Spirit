# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db.models import F

from spirit.models import TopicPollChoice
from ..topic_poll import topic_poll_post_vote, topic_poll_pre_vote


def poll_pre_vote(sender, poll, user, **kwargs):
    TopicPollChoice.objects.filter(poll=poll, votes__user=user)\
        .update(vote_count=F('vote_count') - 1)


def poll_post_vote(sender, poll, user, **kwargs):
    TopicPollChoice.objects.filter(poll=poll, votes__user=user)\
        .update(vote_count=F('vote_count') + 1)


topic_poll_pre_vote.connect(poll_pre_vote, dispatch_uid=__name__)
topic_poll_post_vote.connect(poll_post_vote, dispatch_uid=__name__)
