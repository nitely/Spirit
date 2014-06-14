#-*- coding: utf-8 -*-

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.conf import settings


REASON_CHOICES = (
    (0, _("Spam")),
    (1, _("Other")),
)


class CommentFlag(models.Model):

    moderator = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True)
    comment = models.OneToOneField('spirit.Comment')

    date = models.DateTimeField(auto_now_add=True)
    is_closed = models.BooleanField(default=False)

    class Meta:
        app_label = 'spirit'
        ordering = ['-date', ]
        verbose_name = _("comment flag")
        verbose_name_plural = _("comments flags")

    #def get_absolute_url(self):
        #pass

    def __unicode__(self):
        return "%s flagged" % self.comment


class Flag(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    comment = models.ForeignKey('spirit.Comment')

    date = models.DateTimeField(auto_now_add=True)
    reason = models.IntegerField(_("reason"), choices=REASON_CHOICES)
    body = models.TextField(_("body"), blank=True)

    class Meta:
        app_label = 'spirit'
        unique_together = ('user', 'comment')
        ordering = ['-date', ]
        verbose_name = _("flag")
        verbose_name_plural = _("flags")

    def __unicode__(self):
        return "%s flagged %s" % (self.user, self.comment)