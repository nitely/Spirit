# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings

from haystack import indexes

from spirit.models.topic import Topic


class TopicIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    category_id = indexes.IntegerField(model_attr='category_id')
    is_removed = indexes.BooleanField(model_attr='is_removed')
    is_category_removed = indexes.BooleanField(model_attr='category__is_removed')
    is_subcategory_removed = indexes.BooleanField(model_attr='category__parent__is_removed', default=False)

    def get_model(self):
        return Topic

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        topics = super(TopicIndex, self).index_queryset(using=using)
        return topics.exclude(category_id=settings.ST_TOPIC_PRIVATE_CATEGORY_PK)
