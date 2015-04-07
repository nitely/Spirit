# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class TopicFavorite(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    topic = models.ForeignKey('spirit.Topic')

    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'topic')
        ordering = ['-date', '-pk']
        verbose_name = _("favorite")
        verbose_name_plural = _("favorites")

    def __str__(self):
        return "%s bookmarked %s" % (self.user, self.topic)
