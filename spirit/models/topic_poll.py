#-*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.conf import settings


class TopicPoll(models.Model):

    topic = models.OneToOneField('spirit.Topic', verbose_name=_("topic"), primary_key=True, related_name='poll')

    date = models.DateTimeField(auto_now_add=True)
    choice_limit = models.PositiveIntegerField(_("choice limit"), default=1)
    is_closed = models.BooleanField(default=False)

    class Meta:
        app_label = 'spirit'
        verbose_name = _("topic poll")
        verbose_name_plural = _("topics polls")

    def get_absolute_url(self):
        return self.topic.get_absolute_url()

    def __unicode__(self):
        return "poll at topic #%s" % self.topic.pk


class TopicPollChoice(models.Model):

    poll = models.ForeignKey(TopicPoll, verbose_name=_("poll"), related_name='choices')

    description = models.CharField(_("choice description"), max_length=255)
    vote_count = models.PositiveIntegerField(_("vote count"), default=0)

    class Meta:
        app_label = 'spirit'
        verbose_name = _("poll choice")
        verbose_name_plural = _("poll choices")

    def __unicode__(self):
        return "poll choice %s at topic #%s" % (self.pk, self.poll.topic.pk)


class TopicPollVote(models.Model):

    choice = models.ForeignKey(TopicPollChoice, verbose_name=_("poll choice"), related_name='votes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("voter"))

    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'spirit'
        unique_together = ('user', 'choice')
        verbose_name = _("poll vote")
        verbose_name_plural = _("poll votes")

    def __unicode__(self):
        return "poll vote %s" % self.pk