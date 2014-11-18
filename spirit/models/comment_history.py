# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.utils.encoding import python_2_unicode_compatible

from spirit.signals.comment import comment_pre_update, comment_post_update


@python_2_unicode_compatible
class CommentHistory(models.Model):

    comment_fk = models.ForeignKey('spirit.Comment', verbose_name=_("original comment"))

    comment_html = models.TextField(_("comment html"))
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', ]
        verbose_name = _("comment history")
        verbose_name_plural = _("comments history")

    def get_absolute_url(self):
        return reverse('spirit:comment-history', kwargs={'pk': str(self.id), })

    def __str__(self):
        return "%s: %s..." % (self.comment_fk.user.username, self.comment_html[:50])


def comment_pre_update_handler(sender, comment, **kwargs):
    # save original comment
    exists = CommentHistory.objects.filter(comment_fk=comment).exists()

    if not exists:
        CommentHistory.objects.create(comment_fk=comment, comment_html=comment.comment_html, date=comment.date)


def comment_post_update_handler(sender, comment, **kwargs):
    CommentHistory.objects.create(comment_fk=comment, comment_html=comment.comment_html)


comment_pre_update.connect(comment_pre_update_handler, dispatch_uid=__name__)
comment_post_update.connect(comment_post_update_handler, dispatch_uid=__name__)
