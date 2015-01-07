# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils.encoding import python_2_unicode_compatible

from ..managers.comment import CommentQuerySet


COMMENT_MAX_LEN = 3000  # changing this needs migration

COMMENT, MOVED, CLOSED, UNCLOSED, PINNED, UNPINNED = range(6)

ACTION = (
    (COMMENT, _("comment")),
    (MOVED, _("topic moved")),
    (CLOSED, _("topic closed")),
    (UNCLOSED, _("topic unclosed")),
    (PINNED, _("topic pinned")),
    (UNPINNED, _("topic unpinned")),
)


@python_2_unicode_compatible
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

    objects = CommentQuerySet.as_manager()

    class Meta:
        ordering = ['-date', '-pk']
        verbose_name = _("comment")
        verbose_name_plural = _("comments")

    def __str__(self):
        return "%s: %s..." % (self.user.username, self.comment[:50])

    def get_absolute_url(self):
        return reverse('spirit:comment-find', kwargs={'pk': str(self.id), })

    @property
    def like(self):
        # *likes* is dinamically created by manager.with_likes()
        try:
            assert len(self.likes) <= 1, "Panic, too many likes"
            return self.likes[0]
        except (AttributeError, IndexError):
            return
