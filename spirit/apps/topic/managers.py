# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.shortcuts import get_object_or_404
from django.db.models import Q, Prefetch

from spirit.apps.comment.bookmark.models import CommentBookmark


class TopicQuerySet(models.QuerySet):

    def unremoved(self):
        return self.filter(Q(category__parent=None) | Q(category__parent__is_removed=False),
                           category__is_removed=False,
                           is_removed=False)

    def public(self):
        return self.filter(category__is_private=False)

    def visible(self):
        return self.unremoved().public()

    def opened(self):
        return self.filter(is_closed=False)

    def for_category(self, category):
        if category.is_subcategory:
            return self.filter(category=category)

        return self.filter(Q(category=category) | Q(category__parent=category))

    def _access(self, user):
        return self.filter(Q(category__is_private=False) | Q(topics_private__user=user))

    def for_access(self, user):
        return self.unremoved()._access(user=user)

    def for_unread(self, user):
        return self.filter(topicunread__user=user,
                           topicunread__is_read=False)

    def with_bookmarks(self, user):
        if not user.is_authenticated():
            return self

        user_bookmarks = CommentBookmark.objects\
            .filter(user=user)\
            .select_related('topic')
        prefetch = Prefetch("commentbookmark_set", queryset=user_bookmarks, to_attr='bookmarks')
        return self.prefetch_related(prefetch)

    def get_public_or_404(self, pk, user):
        if user.is_authenticated() and user.st.is_moderator:
            return get_object_or_404(self.public()
                                     .select_related('category__parent'),
                                     pk=pk)
        else:
            return get_object_or_404(self.visible()
                                     .select_related('category__parent'),
                                     pk=pk)

    def for_update_or_404(self, pk, user):
        if user.st.is_moderator:
            return get_object_or_404(self.public(), pk=pk)
        else:
            return get_object_or_404(self.visible().opened(), pk=pk, user=user)
