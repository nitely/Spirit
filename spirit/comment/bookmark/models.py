# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import gettext_lazy as _

from djconfig import config

from ...core.conf import settings
from ...core.utils import paginator
from ...core.utils.db import create_or_none


class CommentBookmark(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='st_comment_bookmarks',
        on_delete=models.CASCADE)
    topic = models.ForeignKey(
        'spirit_topic.Topic',
        on_delete=models.CASCADE)

    comment_number = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('user', 'topic')
        verbose_name = _("comment bookmark")
        verbose_name_plural = _("comments bookmarks")

    def _get_url(self, comment_number=None):
        comment_number = comment_number or self.comment_number
        return paginator.get_url(
            url=self.topic.get_absolute_url(),
            obj_number=comment_number,
            per_page=config.comments_per_page,
            page_var='page')

    def get_absolute_url(self):
        return self._get_url()

    def get_new_comment_url(self):
        comment_number = self.comment_number + 1
        return self._get_url(comment_number=comment_number)

    @staticmethod
    def page_to_comment_number(page_number):
        try:
            page_number = int(page_number)
        except ValueError:
            return

        return config.comments_per_page * (page_number - 1) + 1

    @classmethod
    def increase_to(cls, user, topic, comment_number):
        """
        Increment to comment_number if it's greater \
        than the current one. Return ``True`` if \
        bookmark was updated, return ``False`` otherwise
        """
        assert user.is_authenticated
        return bool(
            cls.objects
            .filter(
                user=user,
                topic=topic,
                comment_number__lt=comment_number)
            .update(comment_number=comment_number))

    @classmethod
    def increase_or_create(cls, user, topic, comment_number):
        """
        Increment to comment_number if it's greater \
        than the current one. Return ``True`` if \
        bookmark was updated/created, return ``False`` \
        otherwise. This operation is atomic
        """
        if not user.is_authenticated:
            return False
        if comment_number is None:
            return False

        kwargs = dict(
            user=user,
            topic=topic,
            comment_number=comment_number)
        # Due to `comment_number__lt` we can't do better than this,
        # both queries run almost always
        return (
            bool(create_or_none(cls, **kwargs)) or
            cls.increase_to(**kwargs))
