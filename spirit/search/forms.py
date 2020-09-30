# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils.encoding import smart_str

from haystack.forms import SearchForm
from haystack.query import EmptySearchQuerySet

from ..core.conf import settings
from ..topic.models import Topic
from ..category.models import Category


class BaseSearchForm(SearchForm):

    def clean_q(self):
        q = self.cleaned_data['q']

        if len(q) < settings.ST_SEARCH_QUERY_MIN_LEN:
            raise forms.ValidationError(
                _("Your search must contain at "
                  "least %(length)s characters.") % {
                    'length': settings.ST_SEARCH_QUERY_MIN_LEN})

        return q


class BasicSearchForm(BaseSearchForm):

    def search(self):
        sqs = super(BasicSearchForm, self).search()

        if isinstance(sqs, EmptySearchQuerySet):
            return sqs

        topics = sqs.models(Topic)

        # See: haystack pull #1141 and #1093
        # querying False won't work on elastic
        return topics.filter(is_removed=0)


class AdvancedSearchForm(BaseSearchForm):

    category = forms.ModelMultipleChoiceField(
        queryset=Category.objects.visible(),
        required=False,
        label=_('Filter by'),
        widget=forms.CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        super(AdvancedSearchForm, self).__init__(*args, **kwargs)
        self.fields['category'].label_from_instance = (
            lambda obj: smart_str(obj.title))
        self.fields['q'].widget.attrs.update({
            'autofocus': ''})

    def search(self):
        sqs = super(AdvancedSearchForm, self).search()

        if isinstance(sqs, EmptySearchQuerySet):
            return sqs

        topics = sqs.models(Topic)
        categories = self.cleaned_data['category']

        if categories:
            topics = topics.filter(
                category_id__in=[c.pk for c in categories])

        # See: haystack pull #1141 and #1093
        # querying False won't work on elastic
        return topics.filter(is_removed=0)
