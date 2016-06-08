# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings

from haystack import indexes

from ..topic.models import Topic


class TopicIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(document=True, use_template=True)
    category_id = indexes.IntegerField(model_attr='category_id')
    is_removed = indexes.BooleanField()

    title = indexes.CharField(model_attr='title', indexed=False)
    slug = indexes.CharField(model_attr='slug', null=True, indexed=False)
    main_category_name = indexes.CharField(indexed=False)
    comment_count = indexes.IntegerField(model_attr='comment_count', indexed=False)

    # Overridden
    def get_model(self):
        return Topic

    # Overridden
    def index_queryset(self, using=None):
        return (self.get_model().objects
                .all()
                .exclude(category_id=settings.ST_TOPIC_PRIVATE_CATEGORY_PK)
                .select_related('category__parent'))

    # Overridden
    def get_updated_field(self):
        """
        This specify what topics should be indexed,\
        based on the last time they were updated.

        Topics will be re-indexed when a new comment\
        is posted. To re-index deleted topics,\
        a full re-index must be ran.

        :return: Last updated name field
        """
        # todo: override build_queryset, and filter by comment
        # updated_at, topic.updated_at, category.updated_at
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

    def prepare_main_category_name(self, obj):
        """
        Populate the ``category_name`` index field\
        with the main category name

        :param obj: Topic
        :return: main category name
        """
        return obj.main_category.title
