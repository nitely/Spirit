# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils.encoding import python_2_unicode_compatible

from spirit.managers.topic import TopicManager
from spirit.utils.models import AutoSlugField


@python_2_unicode_compatible
class Topic(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("user"))
    category = models.ForeignKey('spirit.Category', verbose_name=_("category"))

    title = models.CharField(_("title"), max_length=75)
    slug = AutoSlugField(populate_from="title", db_index=False, blank=True)
    date = models.DateTimeField(_("date"), auto_now_add=True)
    last_active = models.DateTimeField(_("last active"), auto_now_add=True)
    is_pinned = models.BooleanField(_("pinned"), default=False)
    is_closed = models.BooleanField(_("closed"), default=False)
    is_removed = models.BooleanField(default=False)

    view_count = models.PositiveIntegerField(_("views count"), default=0)
    comment_count = models.PositiveIntegerField(_("comment count"), default=0)

    objects = TopicManager()

    class Meta:
        ordering = ['-last_active', ]
        verbose_name = _("topic")
        verbose_name_plural = _("topics")

    def get_absolute_url(self):
        if self.category_id == settings.ST_TOPIC_PRIVATE_CATEGORY_PK:
            return reverse('spirit:private-detail', kwargs={'topic_id': str(self.id), 'slug': self.slug})

        return reverse('spirit:topic-detail', kwargs={'pk': str(self.id), 'slug': self.slug})

    @property
    def main_category(self):
        return self.category.parent or self.category

    def __str__(self):
        return self.title
