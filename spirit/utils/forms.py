# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import forms
from django.utils.encoding import smart_text
from django.db.models import Prefetch


class NestedModelChoiceField(forms.ModelChoiceField):
    """A ModelChoiceField that groups parents and childrens"""
    # TODO: subclass ModelChoiceIterator, remove _populate_choices()

    def __init__(self, related_name, parent_field, label_field, *args, **kwargs):
        """
        @related_name: related_name or "FOO_set"
        @parent_field: ForeignKey('self') field, use 'name_id' to save some queries
        @label_field: field for obj representation
        """
        super(NestedModelChoiceField, self).__init__(*args, **kwargs)
        self.related_name = related_name
        self.parent_field = parent_field
        self.label_field = label_field
        self._populate_choices()

    def _populate_choices(self):
        # This is *hackish* but simpler than subclassing ModelChoiceIterator
        choices = [("", self.empty_label), ]
        kwargs = {self.parent_field: None, }
        queryset = self.queryset.filter(**kwargs)\
            .prefetch_related(Prefetch(self.related_name, queryset=self.queryset))

        for parent in queryset:
            choices.append((self.prepare_value(parent), self.label_from_instance(parent)))
            choices.extend([(self.prepare_value(children), self.label_from_instance(children))
                            for children in getattr(parent, self.related_name).all()])

        self.choices = choices

    def label_from_instance(self, obj):
        level_indicator = ""

        if getattr(obj, self.parent_field):
            level_indicator = "--- "

        return "%s%s" % (level_indicator, smart_text(getattr(obj, self.label_field)))
