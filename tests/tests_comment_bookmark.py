# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.test import TestCase, RequestFactory
from django.core.urlresolvers import reverse
from django.template import Template, Context
from django.core.cache import cache
from django.conf import settings

from djconfig import config

from . import utils

from spirit.models.comment_bookmark import CommentBookmark
from spirit.signals.topic import topic_viewed
from spirit.forms.comment_bookmark import BookmarkForm


class CommentBookmarkViewTest(TestCase):

    def setUp(self):
        cache.clear()
        self.user = utils.create_user()
        self.category = utils.create_category()
        self.topic = utils.create_topic(category=self.category, user=self.user)
        self.comment = utils.create_comment(topic=self.topic)

    def test_bookmark_create(self):
        """
        create comment
        """
        utils.login(self)
        form_data = {'comment_number': 999, }
        response = self.client.post(reverse('spirit:bookmark-create', kwargs={'topic_id': self.topic.pk, }),
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest',
                                    data=form_data)
        self.assertEqual(response.status_code, 200)


class CommentBookmarkSignalTest(TestCase):

    def setUp(self):
        cache.clear()
        self.user = utils.create_user()
        self.category = utils.create_category()
        self.topic = utils.create_topic(category=self.category, user=self.user)

        for _ in range(config.comments_per_page * 4):  # 4 pages
            utils.create_comment(user=self.user, topic=self.topic)

    def test_comment_bookmark_topic_page_viewed_handler(self):
        """
        topic_page_viewed_handler signal
        """
        page = 2
        req = RequestFactory().get('/', data={'page': str(page), })
        req.user = self.user
        topic_viewed.send(sender=self.topic.__class__, topic=self.topic, request=req)
        comment_bookmark = CommentBookmark.objects.get(user=self.user, topic=self.topic)
        self.assertEqual(comment_bookmark.comment_number, config.comments_per_page * (page - 1) + 1)

    def test_comment_bookmark_topic_page_viewed_handler_invalid_page(self):
        """
        invalid page
        """
        page = 'im_a_string'
        req = RequestFactory().get('/', data={'page': str(page), })
        req.user = self.user
        topic_viewed.send(sender=self.topic.__class__, topic=self.topic, request=req)
        self.assertEqual(len(CommentBookmark.objects.all()), 0)


class CommentBookmarkFormTest(TestCase):

    def test_form(self):
        form_data = {'comment_number': 999, }
        form = BookmarkForm(data=form_data)
        self.assertEqual(form.is_valid(), True)


class CommentBookmarkTemplateTagsTest(TestCase):

    def setUp(self):
        cache.clear()
        self.user = utils.create_user()
        self.category = utils.create_category()
        self.topic = utils.create_topic(self.category)
        self.comment = utils.create_comment(topic=self.topic)

    def populate_bookmarks(self):
        """
        should populate the topic's bookmark
        """
        bookmark = CommentBookmark.objects.create(user=self.user, topic=self.topic, comment_number=10)
        out = Template(
            "{% load comment_bookmark %}"
            "{% populate_bookmarks topics=topics user=user %}"
            "{{ topics.0.bookmark.get_absolute_url }}"
        ).render(Context({'topics': [self.topic, ], 'user': self.user}))
        self.assertEqual(out, bookmark.get_absolute_url())
