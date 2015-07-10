# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class CommentLike(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    comment = models.ForeignKey('spirit.Comment', related_name='comment_likes')

    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'comment')
        ordering = ['-date', '-pk']
        verbose_name = _("like")
        verbose_name_plural = _("likes")
        db_table = 'spirit_like_commentlike'  # TODO: remove in Spirit 0.4

    def __str__(self):
        return "%s likes %s" % (self.user, self.comment)

    def get_delete_url(self):
        return reverse('spirit:like-delete', kwargs={'pk': str(self.pk), })
