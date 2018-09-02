# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from .managers import TopicPrivateQuerySet
from ...core.conf import settings


class TopicPrivate(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='st_topics_private',
        on_delete=models.CASCADE)
    topic = models.ForeignKey(
        'spirit_topic.Topic',
        related_name='topics_private',
        on_delete=models.CASCADE)

    date = models.DateTimeField(default=timezone.now)

    objects = TopicPrivateQuerySet.as_manager()

    class Meta:
        unique_together = ('user', 'topic')
        ordering = ['-date', '-pk']
        verbose_name = _("private topic")
        verbose_name_plural = _("private topics")

    def get_absolute_url(self):
        return self.topic.get_absolute_url()
