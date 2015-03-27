# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.db.models import Q


class TopicNotificationQuerySet(models.QuerySet):

    def unremoved(self):
        return self.filter(Q(topic__category__parent=None) | Q(topic__category__parent__is_removed=False),
                           topic__category__is_removed=False,
                           topic__is_removed=False)

    def unread(self):
        return self.filter(is_read=False)

    def _access(self, user):
        return self.filter(Q(topic__category__is_private=False) | Q(topic__topics_private__user=user),
                           user=user)

    def for_access(self, user):
        return self.unremoved()._access(user=user)\
            .exclude(comment=None)

    def read(self, user):
        # returns updated rows count (int)
        return self.filter(user=user)\
            .update(is_read=True)
