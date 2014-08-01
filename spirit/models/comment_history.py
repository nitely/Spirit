#-*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.conf import settings
from django.db.models import signals

from spirit.signals.comment import comment_pre_update, comment_post_update


class CommentHistory(models.Model):

    comment_fk = models.ForeignKey('spirit.Comment', verbose_name=_("original comment"))

    comment_html = models.TextField(_("comment html"))
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'spirit'
        ordering = ['-date', ]
        verbose_name = _("comment history")
        verbose_name_plural = _("comments history")

    def get_absolute_url(self):
        return reverse('spirit:comment-history', kwargs={'pk': str(self.id), })

    def __unicode__(self):
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