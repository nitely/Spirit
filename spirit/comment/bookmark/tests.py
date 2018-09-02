# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.test import TestCase
from django.urls import reverse
from django.template import Template, Context

from djconfig import config

from ...core.tests import utils
from .models import CommentBookmark
from .forms import BookmarkForm


class CommentBookmarkViewTest(TestCase):

    def setUp(self):
        utils.cache_clear()
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
        response = self.client.post(reverse('spirit:comment:bookmark:create', kwargs={'topic_id': self.topic.pk, }),
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest',
                                    data=form_data)
        self.assertEqual(response.status_code, 200)


class CommentBookmarkModelsTest(TestCase):

    def setUp(self):
        utils.cache_clear()
        self.user = utils.create_user()
        self.category = utils.create_category()
        self.topic = utils.create_topic(category=self.category, user=self.user)

        for _ in range(config.comments_per_page * 4):  # 4 pages
            utils.create_comment(user=self.user, topic=self.topic)

    def test_comment_bookmark_get_new_comment_url(self):
        """
        Should return the new comment url (current comment + 1)
        """
        bookmark = CommentBookmark.objects.create(topic=self.topic, user=self.user, comment_number=1)
        self.assertTrue(bookmark.get_absolute_url().endswith('1'))
        self.assertTrue(bookmark.get_new_comment_url().endswith('2'))

    def test_comment_bookmark_update_or_create(self):
        """
        Should update or create the comment number
        """
        page = 2
        CommentBookmark.update_or_create(
            user=self.user,
            topic=self.topic,
            comment_number=CommentBookmark.page_to_comment_number(page)
        )
        comment_bookmark = CommentBookmark.objects.get(user=self.user, topic=self.topic)
        self.assertEqual(comment_bookmark.comment_number, config.comments_per_page * (page - 1) + 1)

    def test_comment_bookmark_update_or_create_invalid_page(self):
        """
        Should do nothing when receiving an invalid page
        """
        page = 'im_a_string'
        CommentBookmark.update_or_create(
            user=self.user,
            topic=self.topic,
            comment_number=CommentBookmark.page_to_comment_number(page)
        )
        self.assertEqual(len(CommentBookmark.objects.all()), 0)


class CommentBookmarkFormTest(TestCase):

    def test_form(self):
        form_data = {'comment_number': 999, }
        form = BookmarkForm(data=form_data)
        self.assertEqual(form.is_valid(), True)


class CommentBookmarkTemplateTagsTest(TestCase):

    def setUp(self):
        utils.cache_clear()
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
