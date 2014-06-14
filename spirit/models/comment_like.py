#-*- coding: utf-8 -*-

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from ..managers.comment_like import CommentLikeManager


class CommentLike(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    comment = models.ForeignKey('spirit.Comment', related_name='comment_likes')

    date = models.DateTimeField(auto_now_add=True)

    objects = CommentLikeManager()

    class Meta:
        app_label = 'spirit'
        unique_together = ('user', 'comment')
        ordering = ['-date', ]
        verbose_name = _("like")
        verbose_name_plural = _("likes")

    def get_delete_url(self):
        return reverse('spirit:like-delete', kwargs={'pk': str(self.pk), })

    def __unicode__(self):
        return "%s likes %s" % (self.user, self.comment)