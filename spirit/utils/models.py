#-*- coding: utf-8 -*-

from django.db.models.fields import SlugField
from django.utils.text import slugify
from django.utils.encoding import smart_text


class AutoSlugField(SlugField):
    """
    Auto populates itself from another field
    """
    def __init__(self, *args, **kwargs):
        self.populate_from = kwargs.pop('populate_from', None)
        super(AutoSlugField, self).__init__(*args, **kwargs)

    def pre_save(self, instance, add):
        default = super(AutoSlugField, self).pre_save(instance, add)

        if default or not add or not self.populate_from:
            return default

        value = getattr(instance, self.populate_from)

        if value is None:
            if self.blank:
                return default

            raise ValueError('Failed to populate slug %s.%s from %s' %
                             (instance._meta.object_name, self.attname, self.populate_from))

        slug = slugify(smart_text(value))[:self.max_length].strip('-')

        # Update the model’s attribute
        setattr(instance, self.attname, slug)

        return slug

    # def deconstruct(self):
        # TODO: django 1.7 requires this