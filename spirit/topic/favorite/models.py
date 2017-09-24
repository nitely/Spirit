# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from ...core.conf import settings


class TopicFavorite(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='st_topic_favorites')
    topic = models.ForeignKey('spirit_topic.Topic')

    date = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'topic')
        ordering = ['-date', '-pk']
        verbose_name = _("favorite")
        verbose_name_plural = _("favorites")
