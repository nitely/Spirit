#-*- coding: utf-8 -*-

from django.db.models import Manager
from django.shortcuts import get_object_or_404
from django.db.models import Q


class CommentManager(Manager):

    def _for_all(self):
        return self.filter(Q(topic__category__parent=None) | Q(topic__category__parent__is_removed=False),
                           topic__category__is_removed=False,
                           topic__is_removed=False,
                           is_removed=False,
                           action=0)\
            .select_related('user')

    def for_all(self):
        return self.filter(is_removed=False, action=0)\
            .select_related('user')

    def for_topic(self, topic):
        return self.filter(topic=topic)\
            .select_related('user')

    def for_public(self):
        return self._for_all()\
            .filter(topic__category__is_private=False)

    def for_user_public(self, user):
        return self.for_public()\
            .filter(user=user)

    def for_access(self, user):
        return self._for_all()\
            .filter(Q(topic__category__is_private=False) | Q(topic__topics_private__user=user))

    def for_update_or_404(self, pk, user):
        if user.is_moderator:
            return get_object_or_404(self, pk=pk)
        else:
            return get_object_or_404(self.for_access(user), user=user, pk=pk)