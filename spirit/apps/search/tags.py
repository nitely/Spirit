# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from spirit.templatetags.registry import register
from spirit.apps.search.forms import BasicSearchForm


@register.inclusion_tag('spirit/search/_form.html')
def render_search_form():
    form = BasicSearchForm()
    return {'form': form, }


@register.assignment_tag()
def get_topics_from_search_result(results):
    # TODO: move to view
    # Since Im only indexing Topics this is ok.
    topics = [r.object for r in results]
    return topics
