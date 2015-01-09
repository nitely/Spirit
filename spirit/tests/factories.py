"""
Factory classes for the tests.

"""
import factory

from spirit import models


class CategoryFactory(factory.DjangoModelFactory):
    """Factory class for the Category model."""

    pk = factory.Sequence(lambda n: n + 1)

    class Meta:
        model = models.Category


class TopicFactory(factory.DjangoModelFactory):
    """Factory class for the Topic model."""

    pk = factory.Sequence(lambda n: n + 1)

    class Meta:
        model = models.Topic


class CommentFactory(factory.DjangoModelFactory):
    """Factory class for the Comment model."""

    pk = factory.Sequence(lambda n: n + 1)

    class Meta:
        model = models.Comment
