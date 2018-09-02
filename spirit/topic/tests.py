# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import datetime
import hashlib

from django.test import TestCase, RequestFactory, override_settings
from django.urls import reverse
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from djconfig.utils import override_djconfig

from ..core.tests import utils
from . import utils as utils_topic
from ..comment.models import MOVED
from .models import Topic
from .forms import TopicForm
from ..comment.models import Comment
from ..comment.bookmark.models import CommentBookmark
from .notification.models import TopicNotification
from .unread.models import TopicUnread


class TopicViewTest(TestCase):

    def setUp(self):
        utils.cache_clear()
        self.user = utils.create_user()

    @override_settings(ST_TESTS_RATELIMIT_NEVER_EXPIRE=True)
    def test_topic_publish(self):
        """
        POST, create topic
        """
        self.assertEqual(len(Topic.objects.all()), 0)

        utils.login(self)
        category = utils.create_category()
        form_data = {'comment': 'foo', 'title': 'foobar', 'category': category.pk}
        response = self.client.post(reverse('spirit:topic:publish'), form_data)
        topic = Topic.objects.last()
        expected_url = topic.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302)
        self.assertEqual(len(Topic.objects.all()), 1)

        # ratelimit
        response = self.client.post(reverse('spirit:topic:publish'), form_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(Topic.objects.all()), 1)

        # get
        response = self.client.get(reverse('spirit:topic:publish'))
        self.assertEqual(response.status_code, 200)

    @override_settings(ST_TESTS_RATELIMIT_NEVER_EXPIRE=True)
    def test_topic_publish_validate(self):
        """
        Should validate all forms even when errors
        """
        self.assertEqual(len(Topic.objects.all()), 0)

        utils.login(self)
        no_data = {}
        response = self.client.post(reverse('spirit:topic:publish'), no_data)
        self.assertEqual(len(Topic.objects.all()), 0)
        self.assertTrue(bool(response.context['form'].errors))
        self.assertTrue(bool(response.context['cform'].errors))
        self.assertEqual(len(list(response.context['messages'])), 0)

        # No rate-limit
        category = utils.create_category()
        form_data = {'comment': 'foo', 'title': 'foobar', 'category': category.pk}
        self.client.post(reverse('spirit:topic:publish'), form_data)
        self.assertEqual(len(Topic.objects.all()), 1)

    def test_topic_publish_long_title(self):
        """
        POST, create topic with long title
        """
        utils.login(self)
        category = utils.create_category()
        title = "a" * 255
        form_data = {'comment': 'foo', 'title': title, 'category': category.pk}
        response = self.client.post(reverse('spirit:topic:publish'),
                                    form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(Topic.objects.all()), 1)
        self.assertEqual(Topic.objects.last().slug, title[:50])

    @override_settings(ST_TESTS_RATELIMIT_NEVER_EXPIRE=True)
    def test_topic_publish_in_category(self):
        """
        POST, create topic in category
        """
        utils.login(self)
        category = utils.create_category()
        form_data = {'comment': 'foo', 'title': 'foobar', 'category': category.pk}
        response = self.client.post(reverse('spirit:topic:publish', kwargs={'category_id': category.pk, }),
                                    form_data)
        topic = Topic.objects.last()
        expected_url = topic.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302)

        # ratelimit
        response = self.client.post(reverse('spirit:topic:publish', kwargs={'category_id': category.pk, }),
                                    form_data)
        self.assertEqual(response.status_code, 200)

    def test_topic_publish_in_subcategory(self):
        """
        POST, create topic in subcategory
        """
        utils.login(self)
        category = utils.create_category()
        subcategory = utils.create_subcategory(category)
        form_data = {'comment': 'foo', 'title': 'foobar', 'category': subcategory.pk}
        response = self.client.post(reverse('spirit:topic:publish', kwargs={'category_id': subcategory.pk, }),
                                    form_data)
        topic = Topic.objects.last()
        expected_url = topic.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302)

    def test_topic_publish_invalid_category(self):
        """
        invalid topic category
        """
        utils.login(self)
        response = self.client.get(reverse('spirit:topic:publish', kwargs={'category_id': str(99), }))
        self.assertEqual(response.status_code, 404)

    @override_settings(ST_DOUBLE_POST_THRESHOLD_MINUTES=10)
    def test_topic_publish_double_post(self):
        """
        Should prevent double posts
        """
        utils.login(self)
        category = utils.create_category()
        topic_title = 'title foobar'

        # First post
        self.client.post(
            reverse('spirit:topic:publish'),
            {'comment': 'foo', 'title': topic_title, 'category': category.pk})
        self.assertEqual(len(Topic.objects.all()), 1)

        # Double post
        utils.cache_clear()  # Clear rate limit
        response = self.client.post(
            reverse('spirit:topic:publish'),
            {'comment': 'foo', 'title': topic_title, 'category': category.pk})
        self.assertEqual(len(Topic.objects.all()), 1)  # Prevented!

        self.assertRedirects(
            response,
            expected_url=category.get_absolute_url(),
            status_code=302,
            target_status_code=200)

        # New post
        utils.cache_clear()  # Clear rate limit
        self.client.post(
            reverse('spirit:topic:publish'),
            {'comment': 'foo', 'title': 'new topic', 'category': category.pk})
        self.assertEqual(len(Topic.objects.all()), 2)

    @override_settings(ST_DOUBLE_POST_THRESHOLD_MINUTES=10)
    def test_topic_publish_same_post_into_another_topic(self):
        """
        Should not prevent from posting the same topic into another category
        """
        utils.login(self)
        category = utils.create_category()
        category_another = utils.create_category()
        topic_title = 'title foobar'

        self.client.post(
            reverse('spirit:topic:publish'),
            {'comment': 'foo', 'title': topic_title, 'category': category.pk})
        self.assertEqual(len(Topic.objects.all()), 1)

        utils.cache_clear()  # Clear rate limit
        self.client.post(
            reverse('spirit:topic:publish'),
            {'comment': 'foo', 'title': topic_title, 'category': category_another.pk})
        self.assertEqual(len(Topic.objects.all()), 2)

    def test_topic_update(self):
        """
        POST, update topic
        """
        utils.login(self)
        category = utils.create_category()
        topic = utils.create_topic(category=category, user=self.user)
        form_data = {'title': 'foobar', }
        response = self.client.post(reverse('spirit:topic:update', kwargs={'pk': topic.pk, }),
                                    form_data)
        self.assertRedirects(response, topic.get_absolute_url(), status_code=302)

    def test_topic_update_create_moderation_action(self):
        """
        POST, topic moved to category
        """
        utils.login(self)
        self.user.st.is_moderator = True
        self.user.save()

        category = utils.create_category()
        topic = utils.create_topic(category=category, user=self.user)
        category2 = utils.create_category()
        form_data = {'title': 'foobar', 'category': category2.pk}
        self.client.post(reverse('spirit:topic:update', kwargs={'pk': topic.pk, }),
                         form_data)
        self.assertEqual(len(Comment.objects.filter(user=self.user, topic_id=topic.pk, action=MOVED)), 1)

    def test_topic_update_invalid_user(self):
        """
        POST, update topic
        """
        utils.login(self)
        category = utils.create_category()
        topic = utils.create_topic(category=category)
        form_data = {'title': 'foobar', }
        response = self.client.post(reverse('spirit:topic:update', kwargs={'pk': topic.pk, }),
                                    form_data)
        self.assertEqual(response.status_code, 404)

    def test_topic_detail_view(self):
        """
        should display topic with comments
        """
        utils.login(self)
        category = utils.create_category()

        topic = utils.create_topic(category=category)
        topic2 = utils.create_topic(category=category)

        comment1 = utils.create_comment(topic=topic)
        comment2 = utils.create_comment(topic=topic)
        utils.create_comment(topic=topic2)

        response = self.client.get(reverse('spirit:topic:detail', kwargs={'pk': topic.pk, 'slug': topic.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['topic'], topic)
        self.assertEqual(list(response.context['comments']), [comment1, comment2])

    @override_djconfig(comments_per_page=2)
    def test_topic_detail_view_paginate(self):
        """
        should display topic with comments, page 1
        """
        utils.login(self)
        category = utils.create_category()

        topic = utils.create_topic(category=category)

        comment1 = utils.create_comment(topic=topic)
        comment2 = utils.create_comment(topic=topic)
        utils.create_comment(topic=topic)  # comment3

        response = self.client.get(reverse('spirit:topic:detail', kwargs={'pk': topic.pk, 'slug': topic.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['comments']), [comment1, comment2])

    def test_topic_detail_viewed(self):
        """
        Calls utils.topic_viewed
        """
        def mocked_topic_viewed(request, topic):
            self._user = request.user
            self._topic = topic

        org_viewed, utils_topic.topic_viewed = utils_topic.topic_viewed, mocked_topic_viewed
        try:
            utils.login(self)
            category = utils.create_category()
            topic = utils.create_topic(category=category, user=self.user)
            response = self.client.get(reverse('spirit:topic:detail', kwargs={'pk': topic.pk, 'slug': topic.slug}))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(self._topic, topic)
            self.assertEqual(self._user, self.user)
        finally:
            utils_topic.topic_viewed = org_viewed

    def test_topic_detail_view_invalid_slug(self):
        """
        invalid slug
        """
        utils.login(self)
        category = utils.create_category()
        topic = utils.create_topic(category=category)
        response = self.client.get(reverse('spirit:topic:detail', kwargs={'pk': topic.pk,
                                                                          'slug': 'bar'}))
        self.assertRedirects(response, topic.get_absolute_url(), status_code=301)

    def test_topic_detail_view_no_slug(self):
        """
        no slug
        """
        utils.login(self)
        category = utils.create_category()
        topic = utils.create_topic(category=category)
        response = self.client.get(reverse('spirit:topic:detail', kwargs={'pk': topic.pk,
                                                                          'slug': ''}))
        self.assertRedirects(response, topic.get_absolute_url(), status_code=301)

    def test_topic_active_view(self):
        """
        topics ordered by activity
        """
        category = utils.create_category()
        topic_a = utils.create_topic(category=category)
        topic_b = utils.create_topic(category=category, user=self.user, view_count=10)
        topic_c = utils.create_topic(category=category)

        Topic.objects.filter(pk=topic_a.pk).update(last_active=timezone.now() - datetime.timedelta(days=10))
        Topic.objects.filter(pk=topic_c.pk).update(last_active=timezone.now() - datetime.timedelta(days=5))

        response = self.client.get(reverse('spirit:topic:index-active'))
        self.assertEqual(list(response.context['topics']), [topic_b, topic_c, topic_a])

    def test_topic_active_view_pinned(self):
        """
        Show globally pinned topics first, regular pinned topics are shown as regular topics
        """
        category = utils.create_category()
        topic_a = utils.create_topic(category=category)
        topic_b = utils.create_topic(category=category, is_pinned=True)
        topic_c = utils.create_topic(category=category)
        topic_d = utils.create_topic(category=category, is_globally_pinned=True)
        # show globally pinned first
        Topic.objects.filter(pk=topic_d.pk).update(last_active=timezone.now() - datetime.timedelta(days=10))

        response = self.client.get(reverse('spirit:topic:index-active'))
        self.assertEqual(list(response.context['topics']), [topic_d, topic_c, topic_b, topic_a])

    def test_topic_active_view_dont_show_private_or_removed(self):
        """
        dont show private topics or removed
        """
        category = utils.create_category()
        category_removed = utils.create_category(is_removed=True)
        subcategory = utils.create_category(parent=category_removed)
        subcategory_removed = utils.create_category(parent=category, is_removed=True)
        utils.create_private_topic()
        utils.create_topic(category=category, is_removed=True)
        utils.create_topic(category=category_removed)
        utils.create_topic(category=subcategory)
        utils.create_topic(category=subcategory_removed)

        response = self.client.get(reverse('spirit:topic:index-active'))
        self.assertEqual(list(response.context['topics']), [])

    def test_topic_active_view_dont_show_not_global(self):
        """
        Should not display non-global categories topics
        """
        # Global subcategories from non-global categories should be displayed
        category_non_global = utils.create_category(is_global=False)
        subcategory_global = utils.create_category(parent=category_non_global)
        utils.create_topic(category=category_non_global)
        topic = utils.create_topic(category=subcategory_global)

        response = self.client.get(reverse('spirit:topic:index-active'))
        self.assertEqual(list(response.context['topics']), [topic])

    def test_topic_active_view_bookmark(self):
        """
        topics with bookmarks
        """
        utils.login(self)
        category = utils.create_category()
        topic = utils.create_topic(category=category, user=self.user)
        bookmark = CommentBookmark.objects.create(topic=topic, user=self.user)

        user2 = utils.create_user()
        CommentBookmark.objects.create(topic=topic, user=user2)

        topic2 = utils.create_topic(category=category, user=self.user)
        CommentBookmark.objects.create(topic=topic2, user=self.user)
        ten_days_ago = timezone.now() - datetime.timedelta(days=10)
        Topic.objects.filter(pk=topic2.pk).update(last_active=ten_days_ago)

        response = self.client.get(reverse('spirit:topic:index-active'))
        self.assertEqual(list(response.context['topics']), [topic, topic2])
        self.assertEqual(response.context['topics'][0].bookmark, bookmark)

    @override_djconfig(topics_per_page=1)
    def test_topic_active_view_paginate(self):
        """
        topics ordered by activity paginated
        """
        category = utils.create_category()
        topic_a = utils.create_topic(category=category)
        topic_b = utils.create_topic(category=category, user=self.user, view_count=10)

        response = self.client.get(reverse('spirit:topic:index-active'))
        self.assertEqual(list(response.context['topics']), [topic_b, ])


class TopicFormTest(TestCase):

    def setUp(self):
        utils.cache_clear()
        self.user = utils.create_user()

    def test_topic_publish(self):
        """
        create topic
        """
        category = utils.create_category()
        subcategory = utils.create_subcategory(category)
        form_data = {'comment': 'foo', 'title': 'foobar',
                     'category': subcategory.pk}
        form = TopicForm(self.user, data=form_data)
        self.assertEqual(form.is_valid(), True)

    def test_topic_publish_invalid_closed_subcategory(self):
        """
        invalid closed subcategory
        """
        category = utils.create_category()
        subcategory = utils.create_subcategory(category, is_closed=True)
        form_data = {'comment': 'foo', 'title': 'foobar',
                     'category': subcategory.pk}
        form = TopicForm(self.user, data=form_data)
        self.assertEqual(form.is_valid(), False)
        self.assertNotIn('category', form.cleaned_data)

    def test_topic_publish_invalid_removed_subcategory(self):
        """
        invalid removed subcategory
        """
        category = utils.create_category()
        subcategory = utils.create_subcategory(category, is_removed=True)
        form_data = {'comment': 'foo', 'title': 'foobar',
                     'category': subcategory.pk}
        form = TopicForm(self.user, data=form_data)
        self.assertEqual(form.is_valid(), False)
        self.assertNotIn('category', form.cleaned_data)

    def test_topic_update(self):
        """
        create update
        """
        category = utils.create_category()
        topic = utils.create_topic(category)
        form_data = {'title': 'foobar', }
        form = TopicForm(self.user, data=form_data, instance=topic)
        self.assertEqual(form.is_valid(), True)

    def test_topic_get_category(self):
        """
        Should return the category
        """
        category = utils.create_category()
        form_data = {
            'title': 'foobar',
            'category': category.pk}
        form = TopicForm(self.user, data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.get_category(), category)

    def test_topic_get_topic_hash(self):
        """
        Should return the topic hash
        """
        category = utils.create_category()
        title = 'title foobar'
        form_data = {
            'title': title,
            'category': category.pk}
        form = TopicForm(self.user, data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.get_topic_hash(),
            hashlib.md5(
                '{}category-{}'
                .format(title, category.pk)
                .encode('utf-8')).hexdigest())

    def test_topic_get_topic_hash_from_field(self):
        """
        Should return the topic hash from form field
        """
        category = utils.create_category()
        topic_hash = '1' * 32
        form_data = {
            'title': 'foobar',
            'category': category.pk,
            'topic_hash': topic_hash}
        form = TopicForm(self.user, data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.get_topic_hash(), topic_hash)

    def test_topic_updates_reindex_at(self):
        """
        Should update reindex_at field
        """
        yesterday = timezone.now() - datetime.timedelta(days=1)
        category = utils.create_category()
        topic = utils.create_topic(category, reindex_at=yesterday)
        self.assertEqual(
            topic.reindex_at,
            yesterday)

        form_data = {'title': 'foobar'}
        form = TopicForm(self.user, data=form_data, instance=topic)
        self.assertEqual(form.is_valid(), True)
        form.save()
        self.assertGreater(
            Topic.objects.get(pk=topic.pk).reindex_at,
            yesterday)


class TopicUtilsTest(TestCase):

    def setUp(self):
        utils.cache_clear()
        self.user = utils.create_user()

    def test_topic_viewed(self):
        """
        * Should update/create the comment bookmark
        * Should mark the topic notification as read
        * Should create or mark the topic (unread) as read
        * Should increase the view_counter
        """
        req = RequestFactory().get('/?page=1')
        req.user = self.user

        category = utils.create_category()
        topic = utils.create_topic(category=category, user=self.user)
        comment = utils.create_comment(topic=topic)
        notification = TopicNotification.objects.create(user=topic.user, topic=topic, comment=comment, is_read=False)
        unread = TopicUnread.objects.create(user=topic.user, topic=topic, is_read=False)
        utils_topic.topic_viewed(req, topic)
        self.assertEqual(len(CommentBookmark.objects.filter(user=self.user, topic=topic)), 1)
        self.assertTrue(TopicNotification.objects.get(pk=notification.pk).is_read)
        self.assertTrue(TopicUnread.objects.get(pk=unread.pk).is_read)
        self.assertEqual(Topic.objects.get(pk=topic.pk).view_count, 1)


class TopicModelsTest(TestCase):

    def setUp(self):
        utils.cache_clear()
        self.user = utils.create_user()
        self.category = utils.create_category()
        self.topic = utils.create_topic(category=self.category, user=self.user)

    def test_topic_increase_view_count(self):
        """
        increase_view_count
        """
        self.topic.increase_view_count()
        self.assertEqual(Topic.objects.get(pk=self.topic.pk).view_count, 1)

    def test_topic_increase_comment_count(self):
        """
        increase_comment_count
        """
        self.topic.increase_comment_count()
        self.assertEqual(Topic.objects.get(pk=self.topic.pk).comment_count, 1)
        self.assertGreater(Topic.objects.get(pk=self.topic.pk).last_active, self.topic.last_active)

    def test_topic_decrease_comment_count(self):
        """
        decrease_comment_count
        """
        Topic.objects.filter(pk=self.topic.pk).update(comment_count=10)
        self.topic.decrease_comment_count()
        self.assertEqual(Topic.objects.get(pk=self.topic.pk).comment_count, 9)

    def test_topic_new_comments_count(self):
        """
        Should return the new replies count
        """
        utils.login(self)
        category = utils.create_category()
        topic = utils.create_topic(category=category, user=self.user, comment_count=1)

        self.assertEqual(
            Topic.objects.filter(pk=topic.pk).with_bookmarks(self.user).first().new_comments_count,
            0
        )

        CommentBookmark.objects.create(topic=topic, user=self.user, comment_number=1)
        self.assertEqual(
            Topic.objects.filter(pk=topic.pk).with_bookmarks(self.user).first().new_comments_count,
            0
        )

        Topic.objects.filter(pk=topic.pk).update(comment_count=2)
        self.assertEqual(
            Topic.objects.filter(pk=topic.pk).with_bookmarks(self.user).first().new_comments_count,
            1
        )

        # topic.comment_count greater than bookmark.comment_number should return 0
        Topic.objects.filter(pk=topic.pk).update(comment_count=0)
        self.assertEqual(
            Topic.objects.filter(pk=topic.pk).with_bookmarks(self.user).first().new_comments_count,
            0
        )

    def test_topic_has_new_comments(self):
        """
        Should return True when there are new replies
        """
        utils.login(self)
        category = utils.create_category()
        topic = utils.create_topic(category=category, user=self.user, comment_count=1)

        self.assertFalse(Topic.objects.filter(pk=topic.pk).with_bookmarks(self.user).first().has_new_comments)

        CommentBookmark.objects.create(topic=topic, user=self.user, comment_number=1)
        self.assertFalse(Topic.objects.filter(pk=topic.pk).with_bookmarks(self.user).first().has_new_comments)

        Topic.objects.filter(pk=topic.pk).update(comment_count=2)
        self.assertTrue(Topic.objects.filter(pk=topic.pk).with_bookmarks(self.user).first().has_new_comments)

    def test_topic_is_visited(self):
        """
        Should return True when the topic has been visited
        """
        utils.login(self)
        category = utils.create_category()
        topic = utils.create_topic(category=category, user=self.user)

        self.assertFalse(Topic.objects.filter(pk=topic.pk).with_bookmarks(self.user).first().is_visited)

        CommentBookmark.objects.create(topic=topic, user=self.user)
        self.assertTrue(Topic.objects.filter(pk=topic.pk).with_bookmarks(self.user).first().is_visited)

    def test_topic_get_bookmark_url(self):
        """
        Should return the bookmark url
        """
        utils.login(self)
        category = utils.create_category()
        topic = utils.create_topic(category=category, user=self.user)

        # No bookmark
        topic_with_bookmark = Topic.objects.filter(pk=topic.pk).with_bookmarks(self.user).first()
        self.assertEqual(topic_with_bookmark.get_bookmark_url(), topic_with_bookmark.get_absolute_url())

        # With bookmark
        CommentBookmark.objects.create(topic=topic, user=self.user, comment_number=1)
        topic_with_bookmark2 = Topic.objects.filter(pk=topic.pk).with_bookmarks(self.user).first()
        self.assertEqual(topic_with_bookmark2.get_bookmark_url(), topic_with_bookmark2.bookmark.get_absolute_url())

        # With bookmark and new comment
        Topic.objects.filter(pk=topic.pk).update(comment_count=2)
        topic_with_bookmark3 = Topic.objects.filter(pk=topic.pk).with_bookmarks(self.user).first()
        self.assertEqual(topic_with_bookmark3.get_bookmark_url(), topic_with_bookmark3.bookmark.get_new_comment_url())
