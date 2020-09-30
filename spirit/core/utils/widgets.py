# -*- coding: utf-8 -*-

from django import forms
from django.utils.encoding import force_str


class MultipleInput(forms.TextInput):
    """
    TextInput widget for input multiple *raw* choices
    """

    def render(self, name, value, *args, **kwargs):
        if value:
            value = ','.join(force_str(v) for v in value)
        else:
            value = ''

        return super(MultipleInput, self).render(
            name, value, *args, **kwargs)

    def value_from_datadict(self, data, files, name, *args, **kwargs):
        value = data.get(name)

        if value:
            return [v.strip() for v in value.split(',')]


class CIMultipleInput(MultipleInput):
    """Case-Insensitive ``MultipleInput`` widget"""

    def value_from_datadict(self, *args, **kwargs):
        value = super(CIMultipleInput, self).value_from_datadict(*args, **kwargs)
        if value:
            return [v.lower() for v in value]


class CITextInput(forms.TextInput):
    """Case-Insensitive ``TextInput`` widget"""

    def value_from_datadict(self, *args, **kwargs):
        value = super(CITextInput, self).value_from_datadict(*args, **kwargs)
        if value:
            return value.lower()
