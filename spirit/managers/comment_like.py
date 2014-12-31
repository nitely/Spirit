# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models


class CommentLikeQuerySet(models.QuerySet):

    def for_user(self, user):
        return self.filter(user=user)\
            .select_related('user', 'comment__user')
