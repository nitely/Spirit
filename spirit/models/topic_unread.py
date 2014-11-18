# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.utils import timezone
from django.db import IntegrityError
from django.utils.encoding import python_2_unicode_compatible

from spirit.signals.comment import comment_posted

from spirit.managers.topic_unread import TopicUnreadManager
from spirit.signals.topic import topic_viewed


@python_2_unicode_compatible
class TopicUnread(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("user"))
    topic = models.ForeignKey('spirit.Topic')

    date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=True)

    objects = TopicUnreadManager()

    class Meta:
        unique_together = ('user', 'topic')
        ordering = ['-date', ]
        verbose_name = _("topic unread")
        verbose_name_plural = _("topics unread")

    def get_absolute_url(self):
        return self.topic.get_absolute_url()

    def __str__(self):
        return "%s read %s" % (self.user, self.topic)


def topic_page_viewed_handler(sender, request, topic, **kwargs):
    if not request.user.is_authenticated():
        return

    # TODO: use update_or_create on django 1.7
    try:
        TopicUnread.objects.create(user=request.user, topic=topic)
    except IntegrityError:
        TopicUnread.objects.filter(user=request.user, topic=topic)\
            .update(is_read=True)


def comment_posted_handler(sender, comment, **kwargs):
    TopicUnread.objects.filter(topic=comment.topic)\
        .exclude(user=comment.user)\
        .update(is_read=False, date=timezone.now())


topic_viewed.connect(topic_page_viewed_handler, dispatch_uid=__name__)
comment_posted.connect(comment_posted_handler, dispatch_uid=__name__)
