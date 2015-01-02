# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.db.models import Q


class CategoryQuerySet(models.QuerySet):

    def unremoved(self):
        return self.filter(Q(parent=None) | Q(parent__is_removed=False),
                           is_removed=False)

    def public(self):
        return self.filter(is_private=False)

    def visible(self):
        return self.unremoved().public()

    def opened(self):
        return self.filter(Q(parent=None) | Q(parent__is_closed=False),
                           is_closed=False)

    def parents(self):
        return self.filter(parent=None)

    def children(self, parent):
        if parent.is_subcategory:
            return self.none()

        return self.filter(parent=parent)
