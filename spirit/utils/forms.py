#-*- coding: utf-8 -*-

from django import forms
from django.utils.html import conditional_escape, mark_safe
from django.utils.encoding import smart_text


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
            .prefetch_related(self.related_name)

        for parent in queryset:
            choices.append((self.prepare_value(parent), self.label_from_instance(parent)))
            choices.extend([(self.prepare_value(children), self.label_from_instance(children))
                            for children in getattr(parent, self.related_name).all()])

        self.choices = choices

    def label_from_instance(self, obj):
        level_indicator = u""

        if getattr(obj, self.parent_field):
            level_indicator = u"--- "

        return mark_safe(level_indicator + conditional_escape(smart_text(getattr(obj, self.label_field))))