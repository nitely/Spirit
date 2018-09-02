# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.test import TestCase
from django.urls import reverse

from ...core.tests import utils
from .models import Flag, CommentFlag
from .forms import FlagForm


class FlagViewTest(TestCase):

    def setUp(self):
        utils.cache_clear()
        self.user = utils.create_user()
        self.category = utils.create_category()
        self.topic = utils.create_topic(category=self.category, user=self.user)
        self.comment = utils.create_comment(user=self.user, topic=self.topic)

    def test_flag_create(self):
        """
        create flag
        """
        utils.login(self)
        form_data = {'reason': "0", }
        response = self.client.post(reverse('spirit:comment:flag:create', kwargs={'comment_id': self.comment.pk, }),
                                    form_data)
        self.assertRedirects(response, self.comment.get_absolute_url(), status_code=302, target_status_code=302)
        self.assertEqual(len(Flag.objects.all()), 1)
        self.assertEqual(len(CommentFlag.objects.all()), 1)


class FlagFormTest(TestCase):

    def setUp(self):
        utils.cache_clear()
        self.user = utils.create_user()
        self.category = utils.create_category()
        self.topic = utils.create_topic(category=self.category, user=self.user)
        self.comment = utils.create_comment(user=self.user, topic=self.topic)

    def test_flag_create(self):
        """
        create flag
        """
        form_data = {'reason': '0', 'body': 'spam comment foo'}
        form = FlagForm(data=form_data)
        form.comment = self.comment
        form.user = self.user
        self.assertEqual(form.is_valid(), True)
        form.save()
        self.assertEqual(len(CommentFlag.objects.all()), 1)
