# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import datetime

from django.test import TestCase, RequestFactory
from django.core.cache import cache
from django.core.urlresolvers import reverse
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
from .poll.forms import TopicPollForm, TopicPollChoiceFormSet
from .notification.models import TopicNotification
from .unread.models import TopicUnread


class TopicViewTest(TestCase):

    def setUp(self):
        cache.clear()
        self.user = utils.create_user()

    def test_topic_publish(self):
        """
        POST, create topic
        """
        utils.login(self)
        category = utils.create_category()
        form_data = {'comment': 'foo', 'title': 'foobar', 'category': category.pk,
                     'choices-TOTAL_FORMS': 2, 'choices-INITIAL_FORMS': 0, 'choice_limit': 1}
        response = self.client.post(reverse('spirit:topic:publish'),
                                    form_data)
        topic = Topic.objects.last()
        expected_url = topic.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302)

        # Make sure it does not creates an empty poll
        self.assertRaises(ObjectDoesNotExist, lambda: topic.poll)

        # ratelimit
        response = self.client.post(reverse('spirit:topic:publish'),
                                    form_data)
        self.assertEqual(response.status_code, 200)

        # get
        response = self.client.get(reverse('spirit:topic:publish'))
        self.assertEqual(response.status_code, 200)

    def test_topic_publish_long_title(self):
        """
        POST, create topic with long title
        """
        utils.login(self)
        category = utils.create_category()
        title = "a" * 255
        form_data = {'comment': 'foo', 'title': title, 'category': category.pk,
                     'choices-TOTAL_FORMS': 2, 'choices-INITIAL_FORMS': 0, 'choice_limit': 1}
        response = self.client.post(reverse('spirit:topic:publish'),
                                    form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(Topic.objects.all()), 1)
        self.assertEqual(Topic.objects.last().slug, title[:50])

    def test_topic_publish_in_category(self):
        """
        POST, create topic in category
        """
        utils.login(self)
        category = utils.create_category()
        form_data = {'comment': 'foo', 'title': 'foobar', 'category': category.pk,
                     'choices-TOTAL_FORMS': 2, 'choices-INITIAL_FORMS': 0, 'choice_limit': 1}
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
        form_data = {'comment': 'foo', 'title': 'foobar', 'category': subcategory.pk,
                     'choices-TOTAL_FORMS': 2, 'choices-INITIAL_FORMS': 0, 'choice_limit': 1}
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

    def test_topic_publish_poll(self):
        """
        POST, create topic + poll
        """
        utils.login(self)
        category = utils.create_category()
        form_data = {'comment': 'foo', 'title': 'foobar', 'category': category.pk,
                     'choices-TOTAL_FORMS': 2, 'choices-INITIAL_FORMS': 0,
                     'choices-0-description': 'op1', 'choices-0-poll': "",
                     'choices-1-description': 'op2', 'choices-1-poll': "",
                     'choice_limit': 2}
        response = self.client.post(reverse('spirit:topic:publish'),
                                    form_data)
        self.assertEqual(response.status_code, 302)
        topic = Topic.objects.last()
        self.assertEqual(topic.poll.choice_limit, 2)
        self.assertEqual(len(topic.poll.choices.all()), 2)

        # get
        response = self.client.get(reverse('spirit:topic:publish'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['pform'], TopicPollForm)
        self.assertIsInstance(response.context['pformset'], TopicPollChoiceFormSet)

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
        cache.clear()
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


class TopicUtilsTest(TestCase):

    def setUp(self):
        cache.clear()
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
        cache.clear()
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
