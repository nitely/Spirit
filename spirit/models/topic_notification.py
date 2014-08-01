#-*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils import timezone
from django.db import IntegrityError

from spirit.signals.comment import comment_posted
from spirit.signals.topic_private import topic_private_post_create, topic_private_access_pre_create
from spirit.signals.topic import topic_viewed

from spirit.managers.topic_notifications import TopicNotificationManager


UNDEFINED, MENTION, COMMENT = xrange(3)

ACTION_CHOICES = (
    (UNDEFINED, _("Undefined")),
    (MENTION, _("Mention")),
    (COMMENT, _("Comment")),
)


class TopicNotification(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("user"))
    topic = models.ForeignKey('spirit.Topic')
    comment = models.ForeignKey('spirit.Comment', null=True, blank=True)

    date = models.DateTimeField(auto_now_add=True)
    action = models.IntegerField(choices=ACTION_CHOICES, default=UNDEFINED)
    is_read = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    objects = TopicNotificationManager()

    class Meta:
        app_label = 'spirit'
        unique_together = ('user', 'topic')
        ordering = ['-date', ]
        verbose_name = _("topic notification")
        verbose_name_plural = _("topics notification")

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

    def __unicode__(self):
        return "%s in %s" % (self.user, self.topic)


def notification_comment_posted_handler(sender, comment, **kwargs):
    # Create Notification for poster
    # if not exists create a dummy one with defaults
    try:
        TopicNotification.objects.get_or_create(user=comment.user, topic=comment.topic,
                                                defaults={'action': COMMENT,
                                                          'is_read': True,
                                                          'is_active': True})
    except IntegrityError:
        pass

    TopicNotification.objects.filter(topic=comment.topic, is_active=True, is_read=True)\
        .exclude(user=comment.user)\
        .update(comment=comment, is_read=False, action=COMMENT, date=timezone.now())


def mention_comment_posted_handler(sender, comment, mentions, **kwargs):
    if not mentions:
        return

    for username, user in mentions.iteritems():
        try:
            TopicNotification.objects.create(user=user, topic=comment.topic,
                                             comment=comment, action=MENTION)
        except IntegrityError:
            pass

    TopicNotification.objects.filter(user__in=mentions.values(), topic=comment.topic, is_read=True)\
        .update(comment=comment, is_read=False, action=MENTION, date=timezone.now())


def comment_posted_handler(sender, comment, mentions, **kwargs):
    notification_comment_posted_handler(sender, comment, **kwargs)
    mention_comment_posted_handler(sender, comment, mentions, **kwargs)


def topic_private_post_create_handler(sender, topics_private, comment, **kwargs):
    # topic.user notification is created on comment_posted
    TopicNotification.objects.bulk_create([TopicNotification(user=tp.user, topic=tp.topic,
                                                             comment=comment, action=COMMENT,
                                                             is_active=True)
                                           for tp in topics_private
                                           if tp.user != tp.topic.user])


def topic_private_access_pre_create_handler(sender, topic, user, **kwargs):
    # TODO: use update_or_create on django 1.7
    # change to post create
    try:
        TopicNotification.objects.create(user=user, topic=topic,
                                         comment=topic.comment_set.last(), action=COMMENT,
                                         is_active=True)
    except IntegrityError:
        pass


def topic_viewed_handler(sender, request, topic, **kwargs):
    if not request.user.is_authenticated():
        return

    TopicNotification.objects.filter(user=request.user, topic=topic)\
        .update(is_read=True)


comment_posted.connect(comment_posted_handler, dispatch_uid=__name__)
topic_private_post_create.connect(topic_private_post_create_handler, dispatch_uid=__name__)
topic_private_access_pre_create.connect(topic_private_access_pre_create_handler, dispatch_uid=__name__)
topic_viewed.connect(topic_viewed_handler, dispatch_uid=__name__)