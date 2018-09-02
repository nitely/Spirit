# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from ...core.conf import settings


class TopicUnread(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='st_topics_unread',
        on_delete=models.CASCADE)
    topic = models.ForeignKey(
        'spirit_topic.Topic',
        on_delete=models.CASCADE)

    date = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'topic')
        ordering = ['-date', '-pk']
        verbose_name = _("topic unread")
        verbose_name_plural = _("topics unread")

    def get_absolute_url(self):
        return self.topic.get_absolute_url()

    @classmethod
    def create_or_mark_as_read(cls, user, topic):
        if not user.is_authenticated:
            return

        return cls.objects.update_or_create(
            user=user,
            topic=topic,
            defaults={'is_read': True})

    @classmethod
    def unread_new_comment(cls, comment):
        (cls.objects
         .filter(topic=comment.topic)
         .exclude(user=comment.user)
         .update(is_read=False, date=timezone.now()))
