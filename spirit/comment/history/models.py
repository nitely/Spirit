# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.utils import timezone


class CommentHistory(models.Model):

    comment_fk = models.ForeignKey('spirit.Comment', verbose_name=_("original comment"))

    comment_html = models.TextField(_("comment html"))
    date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-date', '-pk']
        verbose_name = _("comment history")
        verbose_name_plural = _("comments history")
        db_table = 'spirit_history_commenthistory'  # TODO: remove in Spirit 0.4

    def get_absolute_url(self):
        return reverse('spirit:comment:history:detail', kwargs={'pk': str(self.id), })

    @classmethod
    def create(cls, comment):
        return cls.objects.create(
            comment_fk=comment,
            comment_html=comment.comment_html,
            date=comment.date
        )

    @classmethod
    def create_maybe(cls, comment):
        exists = cls.objects\
            .filter(comment_fk=comment)\
            .exists()

        if not exists:
            return cls.create(comment)
