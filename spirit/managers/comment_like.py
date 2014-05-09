#-*- coding: utf-8 -*-

from django.db.models import Manager


class CommentLikeManager(Manager):

    def for_user(self, user):
        return self.filter(user=user)\
            .select_related('user', 'comment__user')