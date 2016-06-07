# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings

from haystack import indexes

from ..topic.models import Topic


class TopicIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    category_id = indexes.IntegerField(model_attr='category_id')
    is_removed = indexes.BooleanField(model_attr='is_removed')
    is_category_removed = indexes.BooleanField(model_attr='category__is_removed')
    is_subcategory_removed = indexes.BooleanField(
        model_attr='category__parent__is_removed',
        default=False)

    # Overridden
    def get_model(self):
        return Topic

    # Overridden
    def index_queryset(self, using=None):
        return (self.get_model().objects
                .all()
                .exclude(category_id=settings.ST_TOPIC_PRIVATE_CATEGORY_PK))
