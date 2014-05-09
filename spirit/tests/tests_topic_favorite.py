#-*- coding: utf-8 -*-

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.template import Template, Context, TemplateSyntaxError
from django.core.cache import cache

import utils

from spirit.models.topic_favorite import TopicFavorite
from spirit.forms.topic_favorite import FavoriteForm


class FavoriteViewTest(TestCase):

    fixtures = ['spirit_init.json', ]

    # TODO: templatetags test
    def setUp(self):
        cache.clear()
        self.user = utils.create_user()
        self.category = utils.create_category()
        self.topic = utils.create_topic(category=self.category, user=self.user)

    def test_favorite_create(self):
        """
        create favorite
        """
        utils.login(self)
        form_data = {}
        response = self.client.post(reverse('spirit:favorite-create', kwargs={'topic_id': self.topic.pk, }),
                                    form_data)
        self.assertRedirects(response, self.topic.get_absolute_url(), status_code=302)
        self.assertEqual(len(TopicFavorite.objects.all()), 1)

    def test_favorite_create_next(self):
        """
        create favorite using next
        """
        utils.login(self)
        form_data = {'next': '/fakepath/', }
        response = self.client.post(reverse('spirit:favorite-create', kwargs={'topic_id': self.topic.pk, }),
                                    form_data)
        self.assertRedirects(response, '/fakepath/', status_code=302, target_status_code=404)

    def test_favorite_create_invalid(self):
        """
        create favorite invalid
        """
        TopicFavorite.objects.create(user=self.user, topic=self.topic)
        utils.login(self)
        form_data = {'next': '/fakepath/', }
        response = self.client.post(reverse('spirit:favorite-create', kwargs={'topic_id': self.topic.pk, }),
                                    form_data)
        self.assertRedirects(response, '/fakepath/', status_code=302, target_status_code=404)
        self.assertEqual(len(TopicFavorite.objects.all()), 1)

    def test_favorite_delete(self):
        """
        delete favorite
        """
        utils.login(self)
        favorite = TopicFavorite.objects.create(user=self.user, topic=self.topic)
        form_data = {}
        response = self.client.post(reverse('spirit:favorite-delete', kwargs={'pk': favorite.pk, }),
                                    form_data)
        self.assertRedirects(response, self.topic.get_absolute_url(), status_code=302)
        self.assertEqual(len(TopicFavorite.objects.all()), 0)

    def test_favorite_delete_next(self):
        """
        delete favorite next
        """
        utils.login(self)
        favorite = TopicFavorite.objects.create(user=self.user, topic=self.topic)
        form_data = {'next': '/fakepath/', }
        response = self.client.post(reverse('spirit:favorite-delete', kwargs={'pk': favorite.pk, }),
                                    form_data)
        self.assertRedirects(response, '/fakepath/', status_code=302, target_status_code=404)
        self.assertEqual(len(TopicFavorite.objects.all()), 0)


class FavoriteFormTest(TestCase):

    fixtures = ['spirit_init.json', ]

    def setUp(self):
        cache.clear()
        self.user = utils.create_user()
        self.category = utils.create_category()
        self.topic = utils.create_topic(category=self.category, user=self.user)

    def test_favorite_create(self):
        """
        create favorite
        """
        form_data = {}
        form = FavoriteForm(data=form_data)
        form.topic = self.topic
        form.user = self.user
        self.assertEqual(form.is_valid(), True)

    def test_favorite_create_invalid(self):
        """
        create favorite duplicate
        """
        TopicFavorite.objects.create(user=self.user, topic=self.topic)
        form_data = {}
        form = FavoriteForm(data=form_data)
        form.topic = self.topic
        form.user = self.user
        self.assertEqual(form.is_valid(), False)