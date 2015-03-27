# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.shortcuts import get_object_or_404
from django.db.models import Q


class TopicPrivateQuerySet(models.QuerySet):

    def for_delete_or_404(self, pk, user):
        # User is the creator *or* has access
        return get_object_or_404(self,
                                 Q(topic__user=user) | Q(user=user),
                                 pk=pk)

    def for_create_or_404(self, topic_id, user):
        # User is creator *and* has access
        return get_object_or_404(self, topic_id=topic_id, user=user, topic__user=user)
