#-*- coding: utf-8 -*-

from django.db.models import Manager
from django.db.models import Q
from django.shortcuts import get_object_or_404


class CategoryManager(Manager):

    def for_public(self):
        return self.filter(Q(parent=None) | Q(parent__is_removed=False),
                           is_removed=False,
                           is_private=False)

    def for_public_open(self):
        return self.for_public()\
            .filter(Q(parent=None) | Q(parent__is_closed=False),
                    is_closed=False)

    def for_parent(self, parent=None):
        if parent and parent.is_subcategory:
            return self.none()
        else:
            return self.filter(parent=parent,
                               is_removed=False,
                               is_private=False)

    def get_public_or_404(self, pk):
        return get_object_or_404(self.for_public(),
                                 pk=pk)