# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class TopicPoll(models.Model):

    topic = models.OneToOneField('spirit.Topic', verbose_name=_("topic"), primary_key=True, related_name='poll')

    date = models.DateTimeField(auto_now_add=True)
    choice_limit = models.PositiveIntegerField(_("choice limit"), default=1)
    is_closed = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("topic poll")
        verbose_name_plural = _("topics polls")

    def __str__(self):
        return "poll at topic #%s" % self.topic.pk

    def get_absolute_url(self):
        return self.topic.get_absolute_url()

    @property
    def is_multiple_choice(self):
        return self.choice_limit > 1


@python_2_unicode_compatible
class TopicPollChoice(models.Model):

    poll = models.ForeignKey(TopicPoll, verbose_name=_("poll"), related_name='choices')

    description = models.CharField(_("choice description"), max_length=255)
    vote_count = models.PositiveIntegerField(_("vote count"), default=0)

    class Meta:
        verbose_name = _("poll choice")
        verbose_name_plural = _("poll choices")

    def __str__(self):
        return "poll choice %s at topic #%s" % (self.pk, self.poll.topic.pk)


@python_2_unicode_compatible
class TopicPollVote(models.Model):

    choice = models.ForeignKey(TopicPollChoice, verbose_name=_("poll choice"), related_name='votes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("voter"))

    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'choice')
        verbose_name = _("poll vote")
        verbose_name_plural = _("poll votes")

    def __str__(self):
        return "poll vote %s" % self.pk
