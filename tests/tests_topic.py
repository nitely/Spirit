# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime

from django.test import TestCase, RequestFactory
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from djconfig.utils import override_djconfig

from . import utils
from spirit.apps.comment.models import MOVED
from spirit.apps.topic.models import Topic
from spirit.apps.comment.signals import comment_posted, comment_moved
from spirit.apps.topic.signals import topic_viewed
from spirit.apps.topic.forms import TopicForm
from spirit.apps.topic.moderate.signals import topic_post_moderate
from spirit.apps.comment.models import Comment
from spirit.apps.comment.bookmark.models import CommentBookmark
from spirit.apps.topic.poll.forms import TopicPollForm, TopicPollChoiceFormSet


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
        response = self.client.post(reverse('spirit:topic-publish'),
                                    form_data)
        topic = Topic.objects.last()
        expected_url = topic.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302)

        # Make sure it does not creates an empty poll
        self.assertRaises(ObjectDoesNotExist, lambda: topic.poll)

        # ratelimit
        response = self.client.post(reverse('spirit:topic-publish'),
                                    form_data)
        self.assertEqual(response.status_code, 200)

        # get
        response = self.client.get(reverse('spirit:topic-publish'))
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
        response = self.client.post(reverse('spirit:topic-publish'),
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
        response = self.client.post(reverse('spirit:topic-publish', kwargs={'category_id': category.pk, }),
                                    form_data)
        topic = Topic.objects.last()
        expected_url = topic.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302)

        # ratelimit
        response = self.client.post(reverse('spirit:topic-publish', kwargs={'category_id': category.pk, }),
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
        response = self.client.post(reverse('spirit:topic-publish', kwargs={'category_id': subcategory.pk, }),
                                    form_data)
        topic = Topic.objects.last()
        expected_url = topic.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302)

    def test_topic_publish_invalid_category(self):
        """
        invalid topic category
        """
        utils.login(self)
        response = self.client.get(reverse('spirit:topic-publish', kwargs={'category_id': str(99), }))
        self.assertEqual(response.status_code, 404)

    def test_topic_publish_comment_posted_signals(self):
        """
        send publish_comment_posted signal
        """
        def comment_posted_handler(sender, comment, **kwargs):
            self._comment = repr(comment)
        comment_posted.connect(comment_posted_handler)

        utils.login(self)

        category = utils.create_category()
        form_data = {'title': 'foobar', 'category': category.pk, 'comment': 'foo',
                     'choices-TOTAL_FORMS': 2, 'choices-INITIAL_FORMS': 0, 'choice_limit': 1}
        response = self.client.post(reverse('spirit:topic-publish'),
                                    form_data)
        self.assertEqual(response.status_code, 302)
        comment = Comment.objects.last()
        self.assertEqual(self._comment, repr(comment))

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
        response = self.client.post(reverse('spirit:topic-publish'),
                                    form_data)
        self.assertEqual(response.status_code, 302)
        topic = Topic.objects.last()
        self.assertEqual(topic.poll.choice_limit, 2)
        self.assertEqual(len(topic.poll.choices.all()), 2)

        # get
        response = self.client.get(reverse('spirit:topic-publish'))
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
        response = self.client.post(reverse('spirit:topic-update', kwargs={'pk': topic.pk, }),
                                    form_data)
        self.assertRedirects(response, topic.get_absolute_url(), status_code=302)

    def test_topic_update_signal(self):
        """
        POST, topic moved to category
        """
        def topic_post_moderate_handler(sender, user, topic, action, **kwargs):
            self._moderate = [repr(user._wrapped), repr(topic), action]
        topic_post_moderate.connect(topic_post_moderate_handler)

        utils.login(self)
        self.user.st.is_moderator = True
        self.user.save()

        category = utils.create_category()
        topic = utils.create_topic(category=category, user=self.user)
        category2 = utils.create_category()
        form_data = {'title': 'foobar', 'category': category2.pk}
        self.client.post(reverse('spirit:topic-update', kwargs={'pk': topic.pk, }),
                         form_data)
        self.assertSequenceEqual(self._moderate, [repr(self.user), repr(Topic.objects.get(pk=topic.pk)), MOVED])

    def test_topic_update_invalid_user(self):
        """
        POST, update topic
        """
        utils.login(self)
        category = utils.create_category()
        topic = utils.create_topic(category=category)
        form_data = {'title': 'foobar', }
        response = self.client.post(reverse('spirit:topic-update', kwargs={'pk': topic.pk, }),
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

        response = self.client.get(reverse('spirit:topic-detail', kwargs={'pk': topic.pk, 'slug': topic.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['topic'], topic)
        self.assertQuerysetEqual(response.context['comments'], map(repr, [comment1, comment2]))

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

        response = self.client.get(reverse('spirit:topic-detail', kwargs={'pk': topic.pk, 'slug': topic.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['comments'], map(repr, [comment1, comment2]))

    def test_topic_detail_view_signals(self):
        """
        send topic view signal
        """
        def topic_viewed_handler(sender, request, topic, **kwargs):
            self._viewed = [request, repr(topic), ]
        topic_viewed.connect(topic_viewed_handler)

        utils.login(self)

        category = utils.create_category()
        topic = utils.create_topic(category=category, user=self.user)
        response = self.client.get(reverse('spirit:topic-detail', kwargs={'pk': topic.pk, 'slug': topic.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertSequenceEqual(self._viewed, [response.context['request'], repr(topic)])

    def test_topic_detail_view_invalid_slug(self):
        """
        invalid slug
        """
        utils.login(self)
        category = utils.create_category()
        topic = utils.create_topic(category=category)
        response = self.client.get(reverse('spirit:topic-detail', kwargs={'pk': topic.pk,
                                                                          'slug': 'bar'}))
        self.assertRedirects(response, topic.get_absolute_url(), status_code=301)

    def test_topic_detail_view_no_slug(self):
        """
        no slug
        """
        utils.login(self)
        category = utils.create_category()
        topic = utils.create_topic(category=category)
        response = self.client.get(reverse('spirit:topic-detail', kwargs={'pk': topic.pk,
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

        response = self.client.get(reverse('spirit:topic-active'))
        self.assertQuerysetEqual(response.context['topics'], map(repr, [topic_b, topic_c, topic_a]))

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

        response = self.client.get(reverse('spirit:topic-active'))
        self.assertQuerysetEqual(response.context['topics'], map(repr, [topic_d, topic_c, topic_b, topic_a]))

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

        response = self.client.get(reverse('spirit:topic-active'))
        self.assertQuerysetEqual(response.context['topics'], [])

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

        response = self.client.get(reverse('spirit:topic-active'))
        self.assertQuerysetEqual(response.context['topics'], map(repr, [topic, topic2]))
        self.assertEqual(response.context['topics'][0].bookmark, bookmark)

    @override_djconfig(topics_per_page=1)
    def test_topic_active_view_paginate(self):
        """
        topics ordered by activity paginated
        """
        category = utils.create_category()
        topic_a = utils.create_topic(category=category)
        topic_b = utils.create_topic(category=category, user=self.user, view_count=10)

        response = self.client.get(reverse('spirit:topic-active'))
        self.assertQuerysetEqual(response.context['topics'], map(repr, [topic_b, ]))


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


class TopicSignalTest(TestCase):

    def setUp(self):
        cache.clear()
        self.user = utils.create_user()
        self.category = utils.create_category()
        self.topic = utils.create_topic(category=self.category, user=self.user)

    def test_topic_page_viewed_handler(self):
        """
        topic_page_viewed_handler signal
        """
        req = RequestFactory().get('/')
        req.user = self.user
        topic_viewed.send(sender=self.topic.__class__, request=req, topic=self.topic)
        self.assertEqual(Topic.objects.get(pk=self.topic.pk).view_count, 1)

    def test_topic_comment_posted_handler(self):
        """
        comment_posted_handler signal
        """
        comment = utils.create_comment(topic=self.topic)
        comment_posted.send(sender=comment.__class__, comment=comment, mentions=None)
        self.assertEqual(Topic.objects.get(pk=self.topic.pk).comment_count, 1)
        self.assertGreater(Topic.objects.get(pk=self.topic.pk).last_active, self.topic.last_active)

    def test_topic_comment_moved_handler(self):
        """
        comment_moved_handler signal
        """
        comment = utils.create_comment(topic=self.topic)
        comment2 = utils.create_comment(topic=self.topic)
        Topic.objects.filter(pk=self.topic.pk).update(comment_count=10)
        comment_moved.send(sender=comment.__class__, comments=[comment, comment2], topic_from=self.topic)
        self.assertEqual(Topic.objects.get(pk=self.topic.pk).comment_count, 8)
