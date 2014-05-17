#-*- coding: utf-8 -*-

from django.db.models import Manager
from django.shortcuts import get_object_or_404
from django.db.models import Q


class TopicManager(Manager):

    def _for_all(self):
        return self.filter(Q(category__parent=None) | Q(category__parent__is_removed=False),
                           category__is_removed=False,
                           is_removed=False)

    def for_public(self):
        return self._for_all()\
            .filter(category__is_private=False)

    def for_public_open(self):
        return self.for_public()\
            .filter(is_closed=False)

    def for_category(self, category):
        if category.is_subcategory:
            return self.filter(category=category,
                               is_removed=False)
        else:
            return self.filter(Q(category=category) | Q(category__parent=category),
                               category__is_removed=False,
                               is_removed=False)

    def get_public_or_404(self, pk, user):
        if user.is_authenticated() and user.is_moderator:
            return get_object_or_404(self
                                     .select_related('category__parent'),
                                     pk=pk,
                                     category__is_private=False)
        else:
            return get_object_or_404(self.for_public()
                                     .select_related('category__parent'),
                                     pk=pk)

    def for_update_or_404(self, pk, user):
        if user.is_moderator:
            return get_object_or_404(self,
                                     pk=pk,
                                     category__is_private=False)
        else:
            return get_object_or_404(self.for_public_open(),
                                     pk=pk,
                                     user=user)

    def for_access(self, user):
        return self._for_all()\
            .filter(Q(category__is_private=False) | Q(topics_private__user=user))

    def for_access_open(self, user):
        return self.for_access(user)\
            .filter(is_closed=False)