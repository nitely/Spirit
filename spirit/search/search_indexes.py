# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db.models import Q

from haystack import indexes

from ..core.conf import settings
from ..topic.models import Topic


# See: django-haystack issue #801
# convert() from search-engine
# stored value to python value,
# so it only matters when using
# search_result.get_stored_fields()
class BooleanField(indexes.BooleanField):

    bool_map = {'true': True, 'false': False}

    def convert(self, value):
        if value is None:
            return None

        if value in self.bool_map:
            return self.bool_map[value]

        return bool(value)


class TopicIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(document=True, use_template=True, stored=False)
    category_id = indexes.IntegerField(model_attr='category_id', stored=False)
    is_removed = BooleanField(stored=False)

    title = indexes.CharField(model_attr='title', indexed=False)
    slug = indexes.CharField(model_attr='slug', indexed=False)
    comment_count = indexes.IntegerField(model_attr='comment_count', indexed=False)
    last_active = indexes.DateTimeField(model_attr='last_active', indexed=False)
    main_category_name = indexes.CharField(indexed=False)

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
    def build_queryset(self, using=None, start_date=None, end_date=None):
        """
        This specify what topics should be indexed,\
        based on the last time they were updated.

        Topics will be re-indexed when a new comment\
        is posted or the topic is modified or the\
        category/subcategory is modified.

        :return: Topic QuerySet filtered by active\
        time and ordered by pk
        """
        lookup_comments = {}
        lookup_topic = {}
        lookup_category = {}
        lookup_subcategory = {}

        if start_date:
            lookup_comments['last_active__gte'] = start_date
            lookup_topic['reindex_at__gte'] = start_date
            lookup_category['category__reindex_at__gte'] = start_date
            lookup_subcategory['category__parent__reindex_at__gte'] = start_date

        if end_date:
            lookup_comments['last_active__lte'] = end_date
            lookup_topic['reindex_at__lte'] = end_date
            lookup_category['category__reindex_at__lte'] = end_date
            lookup_subcategory['category__parent__reindex_at__lte'] = end_date

        return (self.index_queryset(using=using)
                .filter(
                    Q(**lookup_comments) |
                    Q(**lookup_topic) |
                    Q(**lookup_category) |
                    Q(**lookup_subcategory))
                .order_by('pk'))

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
