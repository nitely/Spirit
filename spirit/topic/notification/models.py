# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.utils import timezone

from .managers import TopicNotificationQuerySet


UNDEFINED, MENTION, COMMENT = range(3)

ACTION_CHOICES = (
    (UNDEFINED, _("Undefined")),
    (MENTION, _("Mention")),
    (COMMENT, _("Comment")),
)


class TopicNotification(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("user"))
    topic = models.ForeignKey('spirit.Topic')
    comment = models.ForeignKey('spirit.Comment', null=True, blank=True)

    date = models.DateTimeField(default=timezone.now)
    action = models.IntegerField(choices=ACTION_CHOICES, default=UNDEFINED)
    is_read = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    objects = TopicNotificationQuerySet.as_manager()

    class Meta:
        unique_together = ('user', 'topic')
        ordering = ['-date', '-pk']
        verbose_name = _("topic notification")
        verbose_name_plural = _("topics notification")
        db_table = 'spirit_notification_topicnotification'  # TODO: remove in Spirit 0.4

    def get_absolute_url(self):
        return self.comment.get_absolute_url()

    @property
    def text_action(self):
        return ACTION_CHOICES[self.action][1]

    @property
    def is_mention(self):
        return self.action == MENTION

    @property
    def is_comment(self):
        return self.action == COMMENT

    @classmethod
    def mark_as_read(cls, user, topic):
        if not user.is_authenticated():
            return

        cls.objects\
            .filter(user=user, topic=topic)\
            .update(is_read=True)