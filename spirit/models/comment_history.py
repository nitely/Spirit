# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class CommentHistory(models.Model):

    comment_fk = models.ForeignKey('spirit.Comment', verbose_name=_("original comment"))

    comment_html = models.TextField(_("comment html"))
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-pk']
        verbose_name = _("comment history")
        verbose_name_plural = _("comments history")

    def __str__(self):
        return "%s: %s..." % (self.comment_fk.user.username, self.comment_html[:50])

    def get_absolute_url(self):
        return reverse('spirit:comment-history', kwargs={'pk': str(self.id), })
