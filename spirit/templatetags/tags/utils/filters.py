# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from .. import register


@register.filter
def has_errors(formset):
    """Checks if a FormSet has errors"""
    # TODO: test
    for form in formset:
        if form.errors:
            return True

    return False
