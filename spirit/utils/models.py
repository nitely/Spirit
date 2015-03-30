# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from slugify import slugify as unicode_slugify

from django.db.models.fields import SlugField
from django.utils.encoding import smart_text
from django.utils.text import slugify
from django.conf import settings

__all__ = ['AutoSlugField', ]


class AutoSlugField(SlugField):
    """
    Auto populates itself from another field.

    It behaves like a regular SlugField.
    When populate_from is provided it'll populate itself on creation,
    only if a slug was not provided.
    """

    def __init__(self, *args, **kwargs):
        self.populate_from = kwargs.pop('populate_from', None)
        super(AutoSlugField, self).__init__(*args, **kwargs)

    def pre_save(self, instance, add):
        default = super(AutoSlugField, self).pre_save(instance, add)

        if default or not add or not self.populate_from:
            return default

        inst = instance

        for attr in self.populate_from.split('.'):
            value = getattr(inst, attr)
            inst = value

        if value is None:
            return default

        # TODO: Django 1.9 will support unicode slugs
        if settings.ST_UNICODE_SLUGS:
            # TODO: mark as safe?
            slug = unicode_slugify(smart_text(value), ok='-')
        else:
            slug = slugify(smart_text(value))

        slug = slug[:self.max_length].strip('-')

        # Update the model’s attribute
        setattr(instance, self.attname, slug)

        return slug

    def deconstruct(self):
        name, path, args, kwargs = super(AutoSlugField, self).deconstruct()

        if self.populate_from is not None:
            kwargs['populate_from'] = self.populate_from

        return name, path, args, kwargs
