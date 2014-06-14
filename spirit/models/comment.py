#-*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.conf import settings
from django.db.models import F

from ..signals.comment_like import comment_like_post_create, comment_like_post_delete
from ..signals.topic import topic_post_moderate

from spirit.managers.comment import CommentManager
from ..signals.comment import comment_post_update


COMMENT_MAX_LEN = 3000  # changing this needs migration

COMMENT, MOVED, CLOSED, UNCLOSED, PINNED, UNPINNED = xrange(6)

ACTION = (
    (COMMENT, _("comment")),
    (MOVED, _("topic moved")),
    (CLOSED, _("topic closed")),
    (UNCLOSED, _("topic unclosed")),
    (PINNED, _("topic pinned")),
    (UNPINNED, _("topic unpinned")),
)


class Comment(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("user"))
    topic = models.ForeignKey('spirit.Topic')

    comment = models.TextField(_("comment"), max_length=COMMENT_MAX_LEN)
    comment_html = models.TextField(_("comment html"))
    action = models.IntegerField(_("action"), choices=ACTION, default=COMMENT)
    date = models.DateTimeField(auto_now_add=True)
    is_removed = models.BooleanField(default=False)
    is_modified = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    modified_count = models.PositiveIntegerField(_("modified count"), default=0)
    likes_count = models.PositiveIntegerField(_("likes count"), default=0)

    objects = CommentManager()

    class Meta:
        app_label = 'spirit'
        ordering = ['-date', ]
        verbose_name = _("comment")
        verbose_name_plural = _("comments")

    def get_absolute_url(self):
        return reverse('spirit:comment-find', kwargs={'pk': str(self.id), })

    def __unicode__(self):
        return "%s: %s..." % (self.user.username, self.comment[:50])


def comment_post_update_handler(sender, comment, **kwargs):
    Comment.objects.filter(pk=comment.pk).update(modified_count=F('modified_count') + 1)


def comment_like_post_create_handler(sender, comment, **kwargs):
    Comment.objects.filter(pk=comment.pk).update(likes_count=F('likes_count') + 1)


def comment_like_post_delete_handler(sender, comment, **kwargs):
    Comment.objects.filter(pk=comment.pk).update(likes_count=F('likes_count') - 1)


def topic_post_moderate_handler(sender, user, topic, action, **kwargs):
    Comment.objects.create(user=user, topic=topic, action=action, comment="action", comment_html="action")


comment_post_update.connect(comment_post_update_handler, dispatch_uid=__name__)
comment_like_post_create.connect(comment_like_post_create_handler, dispatch_uid=__name__)
comment_like_post_delete.connect(comment_like_post_delete_handler, dispatch_uid=__name__)
topic_post_moderate.connect(topic_post_moderate_handler, dispatch_uid=__name__)