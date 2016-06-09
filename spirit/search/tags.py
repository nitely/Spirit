# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from ..core.tags.registry import register
from .forms import BasicSearchForm


@register.inclusion_tag('spirit/search/_form.html')
def render_search_form():
    form = BasicSearchForm()
    return {'form': form, }

