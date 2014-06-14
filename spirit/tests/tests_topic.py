#-*- coding: utf-8 -*-

import datetime

from django.test import TestCase, RequestFactory
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings

import utils

from spirit.models.comment import MOVED, CLOSED, UNCLOSED, PINNED, UNPINNED
from spirit.models.topic import Topic, topic_viewed, comment_posted, comment_moved
from spirit.forms.topic import TopicForm
from spirit.signals.topic import topic_post_moderate
from spirit.models.comment import Comment
from spirit.models.category import Category


class TopicViewTest(TestCase):

    fixtures = ['spirit_init.json', ]

    def setUp(self):
        cache.clear()
        self.user = utils.create_user()

    def test_topic_publish(self):
        """
        POST, create topic
        """
        utils.login(self)
        category = utils.create_category()
        form_data = {'comment': 'foo', 'title': 'foobar', 'category': category.pk}
        response = self.client.post(reverse('spirit:topic-publish'),
                                    form_data)
        topic = Topic.objects.last()
        expected_url = topic.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302)

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
        title = "a" * 75
        form_data = {'comment': 'foo', 'title': title, 'category': category.pk}
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
        form_data = {'comment': 'foo', 'title': 'foobar', 'category': category.pk}
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
        form_data = {'comment': 'foo', 'title': 'foobar',
                     'category': subcategory.pk}
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
        form_data = {'title': 'foobar', 'category': category.pk, 'comment': 'foo'}
        response = self.client.post(reverse('spirit:topic-publish'),
                                    form_data)
        self.assertEqual(response.status_code, 302)
        comment = Comment.objects.last()
        self.assertEqual(self._comment, repr(comment))

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
        self.user.is_moderator = True
        self.user.save()

        category = utils.create_category()
        topic = utils.create_topic(category=category, user=self.user)
        category2 = utils.create_category()
        form_data = {'title': 'foobar', 'category': category2.pk}
        response = self.client.post(reverse('spirit:topic-update', kwargs={'pk': topic.pk, }),
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
        should display topic
        """
        utils.login(self)
        category = utils.create_category()
        topic = utils.create_topic(category=category)
        response = self.client.get(reverse('spirit:topic-detail', kwargs={'pk': topic.pk, 'slug': topic.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['topic'], topic)

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
        pinned topics. Only show pinned topics from uncategorized category, even if the category is removed
        """
        category = utils.create_category()
        # show topic from regular category
        topic_a = utils.create_topic(category=category)
        # dont show pinned from regular category
        topic_b = utils.create_topic(category=category, is_pinned=True)

        uncat_category = Category.objects.get(pk=settings.ST_UNCATEGORIZED_CATEGORY_PK)
        # dont show pinned and removed
        topic_c = utils.create_topic(category=uncat_category, is_pinned=True, is_removed=True)
        # show topic from uncategorized category
        topic_d = utils.create_topic(category=uncat_category, is_pinned=True)
        # show pinned first
        Topic.objects.filter(pk=topic_d.pk).update(last_active=timezone.now() - datetime.timedelta(days=10))

        response = self.client.get(reverse('spirit:topic-active'))
        self.assertQuerysetEqual(response.context['topics'], map(repr, [topic_d, topic_a, ]))

        # show topic from uncategorized category even if it is removed
        Category.objects.filter(pk=uncat_category.pk).update(is_removed=True)
        response = self.client.get(reverse('spirit:topic-active'))
        self.assertQuerysetEqual(response.context['topics'], map(repr, [topic_d, topic_a, ]))

    def test_topic_active_view_dont_show_private_or_removed(self):
        """
        dont show private topics or removed
        """
        category = utils.create_category()
        category_removed = utils.create_category(is_removed=True)
        subcategory = utils.create_category(parent=category_removed)
        subcategory_removed = utils.create_category(parent=category, is_removed=True)
        topic_a = utils.create_private_topic()
        topic_b = utils.create_topic(category=category, is_removed=True)
        topic_c = utils.create_topic(category=category_removed)
        topic_d = utils.create_topic(category=subcategory)
        topic_e = utils.create_topic(category=subcategory_removed)

        response = self.client.get(reverse('spirit:topic-active'))
        self.assertQuerysetEqual(response.context['topics'], [])

    def test_topic_moderate_delete(self):
        """
        delete topic
        """
        utils.login(self)
        self.user.is_moderator = True
        self.user.save()

        category = utils.create_category()
        topic = utils.create_topic(category)
        form_data = {}
        response = self.client.post(reverse('spirit:topic-delete', kwargs={'pk': topic.pk, }),
                                    form_data)
        expected_url = topic.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302)
        self.assertTrue(Topic.objects.get(pk=topic.pk).is_removed)

    def test_topic_moderate_undelete(self):
        """
        undelete topic
        """
        utils.login(self)
        self.user.is_moderator = True
        self.user.save()

        category = utils.create_category()
        topic = utils.create_topic(category, is_removed=True)
        form_data = {}
        response = self.client.post(reverse('spirit:topic-undelete', kwargs={'pk': topic.pk, }),
                                    form_data)
        expected_url = topic.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302)
        self.assertFalse(Topic.objects.get(pk=topic.pk).is_removed)

    def test_topic_moderate_lock(self):
        """
        topic lock
        """
        def topic_post_moderate_handler(sender, user, topic, action, **kwargs):
            self._moderate = [repr(user._wrapped), repr(topic), action]
        topic_post_moderate.connect(topic_post_moderate_handler)

        utils.login(self)
        self.user.is_moderator = True
        self.user.save()

        category = utils.create_category()
        topic = utils.create_topic(category)
        form_data = {}
        response = self.client.post(reverse('spirit:topic-lock', kwargs={'pk': topic.pk, }),
                                    form_data)
        expected_url = topic.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302)
        self.assertTrue(Topic.objects.get(pk=topic.pk).is_closed)
        self.assertEqual(self._moderate, [repr(self.user), repr(topic), CLOSED])

    def test_topic_moderate_unlock(self):
        """
        unlock topic
        """
        def topic_post_moderate_handler(sender, user, topic, action, **kwargs):
            self._moderate = [repr(user._wrapped), repr(topic), action]
        topic_post_moderate.connect(topic_post_moderate_handler)

        utils.login(self)
        self.user.is_moderator = True
        self.user.save()

        category = utils.create_category()
        topic = utils.create_topic(category, is_closed=True)
        form_data = {}
        response = self.client.post(reverse('spirit:topic-unlock', kwargs={'pk': topic.pk, }),
                                    form_data)
        expected_url = topic.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302)
        self.assertFalse(Topic.objects.get(pk=topic.pk).is_closed)
        self.assertEqual(self._moderate, [repr(self.user), repr(topic), UNCLOSED])

    def test_topic_moderate_pin(self):
        """
        topic pin
        """
        def topic_post_moderate_handler(sender, user, topic, action, **kwargs):
            self._moderate = [repr(user._wrapped), repr(topic), action]
        topic_post_moderate.connect(topic_post_moderate_handler)

        utils.login(self)
        self.user.is_moderator = True
        self.user.save()

        category = utils.create_category()
        topic = utils.create_topic(category)
        form_data = {}
        response = self.client.post(reverse('spirit:topic-pin', kwargs={'pk': topic.pk, }),
                                    form_data)
        expected_url = topic.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302)
        self.assertTrue(Topic.objects.get(pk=topic.pk).is_pinned)
        self.assertEqual(self._moderate, [repr(self.user), repr(topic), PINNED])

    def test_topic_moderate_unpin(self):
        """
        topic unpin
        """
        def topic_post_moderate_handler(sender, user, topic, action, **kwargs):
            self._moderate = [repr(user._wrapped), repr(topic), action]
        topic_post_moderate.connect(topic_post_moderate_handler)

        utils.login(self)
        self.user.is_moderator = True
        self.user.save()

        category = utils.create_category()
        topic = utils.create_topic(category, is_pinned=True)
        form_data = {}
        response = self.client.post(reverse('spirit:topic-unpin', kwargs={'pk': topic.pk, }),
                                    form_data)
        expected_url = topic.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302)
        self.assertFalse(Topic.objects.get(pk=topic.pk).is_pinned)
        self.assertEqual(self._moderate, [repr(self.user), repr(topic), UNPINNED])


class TopicFormTest(TestCase):

    fixtures = ['spirit_init.json', ]

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

    def test_topic_publish_invalid_subcategory(self):
        """
        invalid subcategory
        """
        category = utils.create_category()
        subcategory = utils.create_subcategory(category, is_closed=True)
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

    fixtures = ['spirit_init.json', ]

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