#-*- coding: utf-8 -*-

from django.forms.widgets import CheckboxInput

from .. import register


@register.filter
def is_checkbox(field):
    if isinstance(field.field.widget, CheckboxInput):
        return True
    else:
        return False