# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db.models import Manager


class TopicUnreadManager(Manager):

    def for_user(self, user):
        return self.filter(user=user, is_read=False, is_removed=False)

    def read(self, user, topic):
        # returns updated rows count (int)
        return self.filter(user=user, topic=topic)\
            .update(is_read=True)
