#-*- coding: utf-8 -*-

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _


class TopicFavorite(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    topic = models.ForeignKey('spirit.Topic')

    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'spirit'
        unique_together = ('user', 'topic')
        ordering = ['-date', ]
        verbose_name = _("favorite")
        verbose_name_plural = _("favorites")

    def __unicode__(self):
        return "%s bookmarked %s" % (self.user, self.topic)