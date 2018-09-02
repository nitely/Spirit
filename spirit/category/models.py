# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from django.utils import timezone

from ..core.conf import settings
from ..core.utils.models import AutoSlugField
from .managers import CategoryQuerySet


class Category(models.Model):
    """
    Category model

    :ivar reindex_at: Last time this model was marked\
    for reindex. It makes the search re-index the topic,\
    it must be set explicitly
    :vartype reindex_at: `:py:class:models.DateTimeField`
    """
    parent = models.ForeignKey(
        'self',
        verbose_name=_("category parent"),
        null=True,
        blank=True,
        on_delete=models.CASCADE)

    title = models.CharField(_("title"), max_length=75)
    slug = AutoSlugField(populate_from="title", db_index=False, blank=True)
    description = models.CharField(_("description"), max_length=255, blank=True)
    color = models.CharField(
        _("color"), max_length=7, blank=True,
        help_text=_("Title color in hex format (i.e: #1aafd0)."))
    reindex_at = models.DateTimeField(_("modified at"), default=timezone.now)

    is_global = models.BooleanField(
        _("global"), default=True,
        help_text=_(
            'Designates whether the topics will be'
            'displayed in the all-categories list.'))
    is_closed = models.BooleanField(_("closed"), default=False)
    is_removed = models.BooleanField(_("removed"), default=False)
    is_private = models.BooleanField(_("private"), default=False)

    objects = CategoryQuerySet.as_manager()

    class Meta:
        ordering = ['title', 'pk']
        verbose_name = _("category")
        verbose_name_plural = _("categories")

    def get_absolute_url(self):
        if self.pk == settings.ST_TOPIC_PRIVATE_CATEGORY_PK:
            return reverse('spirit:topic:private:index')
        else:
            return reverse(
                'spirit:category:detail',
                kwargs={'pk': str(self.id), 'slug': self.slug})

    @property
    def is_subcategory(self):
        if self.parent_id:
            return True
        else:
            return False
