#-*- coding: utf-8 -*-

from django.db.models import Manager
from django.db.models import Q


class TopicNotificationManager(Manager):

    def _for_all(self):
        return self.filter(Q(topic__category__parent=None) | Q(topic__category__parent__is_removed=False),
                           topic__category__is_removed=False,
                           topic__is_removed=False)

    def for_access(self, user):
        return self._for_all()\
            .filter(Q(topic__category__is_private=False) | Q(topic__topics_private__user=user),
                    user=user)\
            .exclude(comment=None)

    def read(self, user):
        # returns updated rows count (int)
        return self.filter(user=user)\
            .update(is_read=True)