# -*- coding: utf-8 -*-

from django.test import TestCase

from .models import (
    AutoSlugPopulateFromModel,
    AutoSlugModel,
    AutoSlugDefaultModel,
    AutoSlugBadPopulateFromModel)


class UtilsModelsTests(TestCase):

    def test_auto_slug_field(self):
        """
        Should behave like a regular SlugField if populate_from is not provided
        """
        foo_model = AutoSlugModel(slug="foo")
        foo_model.save()
        self.assertEqual(foo_model.slug, "foo")

        foo_model = AutoSlugModel()
        foo_model.save()
        self.assertEqual(foo_model.slug, "")

    def test_auto_slug_field_default(self):
        """
        AutoSlugField default
        """
        foo_model = AutoSlugDefaultModel()
        foo_model.save()
        self.assertEqual(foo_model.slug, "foo")

        foo_model = AutoSlugDefaultModel(slug="bar")
        foo_model.save()
        self.assertEqual(foo_model.slug, "bar")

    def test_auto_slug_field_invalid_populate_from(self):
        """
        Should raise AttributeError
        """
        foo_model = AutoSlugBadPopulateFromModel()
        self.assertRaisesMessage(AttributeError, "'AutoSlugBadPopulateFromModel' "
                                                 "object has no attribute 'bad'", foo_model.save)

    def test_auto_slug_field_populate_from(self):
        """
        AutoSlugField populate_from
        """
        title = "a" * 255
        foo_model = AutoSlugPopulateFromModel(title=title)
        foo_model.save()
        self.assertEqual(foo_model.slug, title[:50])

        # update title
        foo_model.title = "foo"
        foo_model.save()
        self.assertEqual(foo_model.slug, title[:50])

        # update slug
        foo_model.slug = "foo"
        foo_model.save()
        self.assertEqual(foo_model.slug, "foo")

        # update slug to blank
        foo_model.slug = ""
        foo_model.save()
        self.assertEqual(foo_model.slug, "")

        # populate_from field is blank
        foo_model = AutoSlugPopulateFromModel()
        self.assertEqual(foo_model.slug, "")

    def test_auto_slug_field_unicode(self):
        """
        AutoSlugField should handle unicode
        """
        title = "愛" * 255
        foo_model = AutoSlugPopulateFromModel(title=title)
        foo_model.save()
        self.assertEqual(foo_model.slug, title[:50])

        title = "áéíóú"
        foo_model = AutoSlugPopulateFromModel(title=title)
        foo_model.save()
        self.assertEqual(foo_model.slug, "áéíóú")

        title = "$~@"
        foo_model = AutoSlugPopulateFromModel(title=title)
        foo_model.save()
        self.assertEqual(foo_model.slug, "")

    def test_auto_slug_field_word_separation(self):
        """
        AutoSlugField not end with "-"
        """
        title = "---"
        foo_model = AutoSlugPopulateFromModel(title=title)
        foo_model.save()
        self.assertEqual(foo_model.slug, "")

        title = "-word-"
        foo_model = AutoSlugPopulateFromModel(title=title)
        foo_model.save()
        self.assertEqual(foo_model.slug, "word")

        title = " -word- "
        foo_model = AutoSlugPopulateFromModel(title=title)
        foo_model.save()
        self.assertEqual(foo_model.slug, "word")

        title = "s-e-p-a-r-a-t-i-o-n-s"
        foo_model = AutoSlugPopulateFromModel(title=title)
        foo_model.save()
        self.assertEqual(foo_model.slug, "s-e-p-a-r-a-t-i-o-n-s")

        title = "s e  p   a    r     a     t    i   o  n s"
        foo_model = AutoSlugPopulateFromModel(title=title)
        foo_model.save()
        self.assertEqual(foo_model.slug, "s-e-p-a-r-a-t-i-o-n-s")
