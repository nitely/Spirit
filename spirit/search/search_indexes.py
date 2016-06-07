# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings

from haystack import indexes

from ..topic.models import Topic


class TopicIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    category_id = indexes.IntegerField(model_attr='category_id')
    is_removed = indexes.BooleanField()

    # Overridden
    def get_model(self):
        return Topic

    # Overridden
    def index_queryset(self, using=None):
        return (self.get_model().objects
                .all()
                .exclude(category_id=settings.ST_TOPIC_PRIVATE_CATEGORY_PK))

    # Overridden
    def get_updated_field(self):
        """
        Topics will be re-indexed when a new comment\
        is added to the topic. To re-index deleted topics,\
        a full re-index must be ran.

        :return: Last updated name field
        """
        return 'last_active'

    def prepare_is_removed(self, obj):
        """
        Populate the ``is_removed`` index field

        :param obj: Topic
        :return: whether the topic is removed or not
        """
        return (obj.is_removed or
                obj.category.is_removed or
                obj.main_category.is_removed)
