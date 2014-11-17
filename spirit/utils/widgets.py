# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import forms
from django.utils.encoding import force_text


class MultipleInput(forms.TextInput):
    """
    TextInput widget for input multiple *raw* choices
    """

    def __init__(self, attrs=None, choices=()):
        # choices is some iterable we do not need, since this is a TextInput
        super(MultipleInput, self).__init__(attrs)

    def render(self, name, value, attrs=None, choices=()):
        if value:
            value = ','.join([force_text(v) for v in value])
        else:
            value = ''

        return super(MultipleInput, self).render(name, value, attrs=attrs)

    def value_from_datadict(self, data, files, name):
        value = data.get(name)

        if value:
            return [v.strip() for v in value.split(',')]
