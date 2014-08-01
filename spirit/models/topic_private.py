#-*- coding: utf-8 -*-

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from spirit.managers.topic_private import TopicPrivateManager


class TopicPrivate(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    topic = models.ForeignKey('spirit.Topic', related_name='topics_private')

    date = models.DateTimeField(auto_now_add=True)

    objects = TopicPrivateManager()

    class Meta:
        app_label = 'spirit'
        unique_together = ('user', 'topic')
        ordering = ['-date', ]
        verbose_name = _("private topic")
        verbose_name_plural = _("private topics")

    def get_absolute_url(self):
        return self.topic.get_absolute_url()

    def __unicode__(self):
        return "%s participes in %s" % (self.user, self.topic)