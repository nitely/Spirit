# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class TopicUnread(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("user"))
    topic = models.ForeignKey('spirit.Topic')

    date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'topic')
        ordering = ['-date', '-pk']
        verbose_name = _("topic unread")
        verbose_name_plural = _("topics unread")

    def __str__(self):
        return "%s read %s" % (self.user, self.topic)

    def get_absolute_url(self):
        return self.topic.get_absolute_url()
