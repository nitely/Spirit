# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.db.models import F
from django.utils import timezone

from ..core.conf import settings
from .managers import CommentQuerySet


class Comment(models.Model):
    COMMENT, MOVED, CLOSED, UNCLOSED, PINNED, UNPINNED = range(6)
    ACTIONS = (
        (COMMENT, _("comment")),
        (MOVED, _("topic moved")),
        (CLOSED, _("topic closed")),
        (UNCLOSED, _("topic unclosed")),
        (PINNED, _("topic pinned")),
        (UNPINNED, _("topic unpinned")))

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='st_comments',
        on_delete=models.CASCADE)
    topic = models.ForeignKey(
        'spirit_topic.Topic',
        on_delete=models.CASCADE)

    comment = models.TextField(_("comment"))
    comment_html = models.TextField(_("comment html"))
    action = models.IntegerField(_("action"), choices=ACTIONS, default=COMMENT)
    date = models.DateTimeField(default=timezone.now)
    is_removed = models.BooleanField(default=False)
    is_modified = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    modified_count = models.PositiveIntegerField(_("modified count"), default=0)
    likes_count = models.PositiveIntegerField(_("likes count"), default=0)

    objects = CommentQuerySet.as_manager()

    class Meta:
        ordering = ['-date', '-pk']
        verbose_name = _("comment")
        verbose_name_plural = _("comments")

    def get_absolute_url(self):
        return reverse('spirit:comment:find', kwargs={'pk': str(self.id), })

    @property
    def like(self):
        # *likes* is dynamically created by manager.with_likes()
        try:
            assert len(self.likes) <= 1, "Panic, too many likes"
            return self.likes[0]
        except (AttributeError, IndexError):
            return

    def increase_modified_count(self):
        (Comment.objects
         .filter(pk=self.pk)
         .update(modified_count=F('modified_count') + 1))

    def increase_likes_count(self):
        (Comment.objects
         .filter(pk=self.pk)
         .update(likes_count=F('likes_count') + 1))

    def decrease_likes_count(self):
        (Comment.objects
         .filter(pk=self.pk, likes_count__gt=0)
         .update(likes_count=F('likes_count') - 1))

    @classmethod
    def create_moderation_action(cls, user, topic, action):
        # TODO: better comment_html text (map to actions), use default language
        return cls.objects.create(
            user=user,
            topic=topic,
            action=action,
            comment="action",
            comment_html="action")

    @classmethod
    def get_last_for_topic(cls, topic_id):
        return (
            cls.objects
                .filter(topic_id=topic_id)
                .order_by('pk')
                .last())
