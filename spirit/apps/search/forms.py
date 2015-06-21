# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from haystack.forms import SearchForm
from haystack.query import EmptySearchQuerySet

from ..topic.models import Topic
from ..category.models import Category


class BaseSearchForm(SearchForm):

    def clean_q(self):
        q = self.cleaned_data['q']

        if len(q) < settings.ST_SEARCH_QUERY_MIN_LEN:
            raise forms.ValidationError(_("Your search must contain at least %(length)s characters.")
                                        % {'length': settings.ST_SEARCH_QUERY_MIN_LEN, })

        return q


class BasicSearchForm(BaseSearchForm):

    def search(self):
        sqs = super(BasicSearchForm, self).search()

        if isinstance(sqs, EmptySearchQuerySet):
            return sqs

        topics = sqs.models(Topic)
        return topics.filter(is_removed=False, is_category_removed=False, is_subcategory_removed=False)


class AdvancedSearchForm(BaseSearchForm):

    category = forms.ModelMultipleChoiceField(queryset=Category.objects.visible(),
                                              required=False,
                                              label=_('Filter by'),
                                              widget=forms.CheckboxSelectMultiple)

    def search(self):
        sqs = super(AdvancedSearchForm, self).search()

        if isinstance(sqs, EmptySearchQuerySet):
            return sqs

        topics = sqs.models(Topic)
        categories = self.cleaned_data['category']

        if categories:
            topics = topics.filter(category_id__in=[c.pk for c in categories])

        return topics.filter(is_removed=False, is_category_removed=False, is_subcategory_removed=False)
