#-*- coding: utf-8 -*-

import datetime

from django.test import TestCase
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.template import Template, Context
from django.conf import settings
from django.utils import timezone

import utils

from spirit.models.category import Category
from spirit.models.topic_private import TopicPrivate
from spirit.forms.topic_private import TopicForPrivateForm, TopicPrivateInviteForm,\
    TopicPrivateManyForm, TopicPrivateJoinForm
from spirit.templatetags.tags.topic_private import render_invite_form
from spirit.views.topic_private import comment_posted
from spirit.models.comment import Comment
from spirit.signals.topic_private import topic_private_post_create, topic_private_access_pre_create
from spirit.models.topic import Topic


class TopicPrivateViewTest(TestCase):

    fixtures = ['spirit_init.json', ]

    def setUp(self):
        cache.clear()
        self.user = utils.create_user()
        self.user2 = utils.create_user()

    def test_private_publish(self):
        """
        POST, create private topic
        """
        utils.login(self)
        form_data = {'comment': 'foo', 'title': 'foobar', 'users': self.user2.username}
        response = self.client.post(reverse('spirit:private-publish'),
                                    form_data)
        private = TopicPrivate.objects.last()
        expected_url = private.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302)

        response = self.client.get(reverse('spirit:private-publish'))
        self.assertEqual(response.status_code, 200)

    def test_private_publish_comment_posted_signals(self):
        """
        send publish_comment_posted signal
        """
        def comment_posted_handler(sender, comment, **kwargs):
            self._comment = repr(comment)
        comment_posted.connect(comment_posted_handler)

        utils.login(self)
        form_data = {'comment': 'foo', 'title': 'foobar', 'users': self.user2.username}
        response = self.client.post(reverse('spirit:private-publish'),
                                    form_data)
        self.assertEqual(response.status_code, 302)
        comment = Comment.objects.last()
        self.assertEqual(self._comment, repr(comment))

    def test_private_publish_topic_private_post_create_signals(self):
        """
        send topic_private_post_create signal
        """
        def topic_private_post_create_handler(sender, topics_private, comment, **kwargs):
            self.assertEqual(len(topics_private), 1)
            tp = topics_private[0]
            self._topic = repr(tp.topic)
            self._user = repr(tp.user)
            self._comment = repr(comment)
        topic_private_post_create.connect(topic_private_post_create_handler)

        utils.login(self)
        form_data = {'comment': 'foo', 'title': 'foobar', 'users': self.user.username}
        response = self.client.post(reverse('spirit:private-publish'),
                                    form_data)
        self.assertEqual(response.status_code, 302)
        topic_private = TopicPrivate.objects.last()
        topic_comment = Comment.objects.last()
        self.assertEqual(self._topic, repr(topic_private.topic))
        self.assertEqual(self._user, repr(self.user))
        self.assertEqual(self._comment, repr(topic_comment))

    def test_private_publish_user(self):
        """
        create private topic with user as initial value
        """
        utils.login(self)
        response = self.client.get(reverse('spirit:private-publish', kwargs={'user_id': self.user2.pk, }))
        self.assertEqual(response.context['tpform'].initial['users'], [self.user2.username, ])

    def test_private_detail(self):
        """
        private topic detail
        """
        utils.login(self)
        private = utils.create_private_topic(user=self.user)
        response = self.client.get(reverse('spirit:private-detail', kwargs={'topic_id': private.topic.pk,
                                                                            'slug': private.topic.slug}))
        self.assertEqual(response.context['topic'], private.topic)

    def test_private_access_create(self):
        """
        private topic access creation
        """
        utils.login(self)
        private = utils.create_private_topic(user=self.user)
        form_data = {'user': self.user2.username, }
        response = self.client.post(reverse('spirit:private-access-create', kwargs={'topic_id': private.topic.pk, }),
                                    form_data)
        expected_url = private.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302)
        self.assertEqual(len(TopicPrivate.objects.filter(user=self.user2, topic=private.topic)), 1)

    def test_private_access_create_invalid(self):
        """
        Only the topic owner should be able to invite
        """
        utils.login(self)
        private = utils.create_private_topic(user=self.user2)
        TopicPrivate.objects.create(user=self.user, topic=private.topic)
        user = utils.create_user()
        form_data = {'user': user.username, }
        response = self.client.post(reverse('spirit:private-access-create', kwargs={'topic_id': private.topic.pk, }),
                                    form_data)
        self.assertEqual(response.status_code, 404)

    def test_private_access_create_pre_create_signal(self):
        """
        send topic_private_access_pre_create signal
        """
        def topic_private_access_pre_create_handler(sender, topic, user, **kwargs):
            self._topic = repr(topic)
            self._user = repr(user)
        topic_private_access_pre_create.connect(topic_private_access_pre_create_handler)

        utils.login(self)
        private = utils.create_private_topic(user=self.user)
        form_data = {'user': self.user2.username, }
        response = self.client.post(reverse('spirit:private-access-create', kwargs={'topic_id': private.topic.pk, }),
                                    form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self._topic, repr(private.topic))
        self.assertEqual(self._user, repr(self.user2))

    def test_private_access_delete(self):
        """
        private topic access deletion
        """
        utils.login(self)
        private = utils.create_private_topic(user=self.user)
        private2 = TopicPrivate.objects.create(user=self.user2, topic=private.topic)
        form_data = {}
        response = self.client.post(reverse('spirit:private-access-remove', kwargs={'pk': private2.pk, }),
                                    form_data)
        expected_url = private.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302)

    def test_private_access_delete_invalid(self):
        """
        Only the topic owner should be able to remove accesses
        """
        utils.login(self)
        private = utils.create_private_topic(user=self.user2)
        TopicPrivate.objects.create(user=self.user, topic=private.topic)
        form_data = {}
        response = self.client.post(reverse('spirit:private-access-remove', kwargs={'pk': private.pk, }),
                                    form_data)
        self.assertEqual(response.status_code, 404)

    def test_private_access_delete_leave(self):
        """
        user should be able to remove himself
        """
        utils.login(self)
        private = utils.create_private_topic(user=self.user2)
        private2_leave = TopicPrivate.objects.create(user=self.user, topic=private.topic)
        form_data = {}
        response = self.client.post(reverse('spirit:private-access-remove', kwargs={'pk': private2_leave.pk, }),
                                    form_data)
        expected_url = reverse("spirit:private-list")
        self.assertRedirects(response, expected_url, status_code=302)

    def test_private_list(self):
        """
        private topic list
        """
        private = utils.create_private_topic(user=self.user)
        # dont show private topics from other users
        private2 = TopicPrivate.objects.create(user=self.user2, topic=private.topic)
        # dont show topics from other categories
        category = utils.create_category()
        topic = utils.create_topic(category, user=self.user)

        utils.login(self)
        response = self.client.get(reverse('spirit:private-list'))
        self.assertQuerysetEqual(response.context['topics'], [repr(private.topic), ])

    def test_private_list_order_topics(self):
        """
        private topic list ordered by last active
        """
        private_a = utils.create_private_topic(user=self.user)
        private_b = utils.create_private_topic(user=self.user)
        private_c = utils.create_private_topic(user=self.user)

        Topic.objects.filter(pk=private_a.topic.pk).update(last_active=timezone.now() - datetime.timedelta(days=10))
        Topic.objects.filter(pk=private_c.topic.pk).update(last_active=timezone.now() - datetime.timedelta(days=5))

        utils.login(self)
        response = self.client.get(reverse('spirit:private-list'))
        self.assertQuerysetEqual(response.context['topics'], map(repr, [private_b.topic, private_c.topic,
                                                                        private_a.topic]))

    def test_private_join(self):
        """
        private topic join
        """
        private = utils.create_private_topic(user=self.user)
        private.delete()

        utils.login(self)
        form_data = {}
        response = self.client.post(reverse('spirit:private-join', kwargs={'topic_id': private.topic.pk, }),
                                    form_data)
        expected_url = private.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302)

        response = self.client.get(reverse('spirit:private-join', kwargs={'topic_id': private.topic.pk, }))
        self.assertEqual(response.status_code, 200)

    def test_private_join_invalid_regular_topic(self):
        """
        Only topics from the category private can be rejoined
        """
        category = utils.create_category()
        topic = utils.create_topic(category, user=self.user)

        utils.login(self)
        form_data = {}
        response = self.client.post(reverse('spirit:private-join', kwargs={'topic_id': topic.pk, }),
                                    form_data)
        self.assertEqual(response.status_code, 404)

    def test_private_join_invalid_not_owner(self):
        """
        Only topic creators/owners can rejoin
        """
        private = utils.create_private_topic(user=self.user2)

        utils.login(self)
        form_data = {}
        response = self.client.post(reverse('spirit:private-join', kwargs={'topic_id': private.topic.pk, }),
                                    form_data)
        self.assertEqual(response.status_code, 404)

    def test_private_join_access_pre_create_signal(self):
        """
        send topic_private_access_pre_create signal
        """
        def topic_private_access_pre_create_handler(sender, topic, user, **kwargs):
            self._topic = repr(topic)
            self._user_pk = user.pk
        topic_private_access_pre_create.connect(topic_private_access_pre_create_handler)

        private = utils.create_private_topic(user=self.user)
        private.delete()

        utils.login(self)
        form_data = {}
        response = self.client.post(reverse('spirit:private-join', kwargs={'topic_id': private.topic.pk, }),
                                    form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self._topic, repr(private.topic))
        self.assertEqual(self._user_pk, self.user.pk)

    def test_private_created_list(self):
        """
        private topic created list, shows only the private topics the user is no longer participating
        """
        category = utils.create_category()
        regular_topic = utils.create_topic(category, user=self.user)
        # it's the owner, left the topic
        private = utils.create_private_topic(user=self.user)
        private.delete()
        # has access and is the owner
        private2 = utils.create_private_topic(user=self.user)
        # does not has access
        private3 = utils.create_private_topic(user=self.user2)
        # has access but it's not owner
        private4 = utils.create_private_topic(user=self.user2)
        TopicPrivate.objects.create(user=self.user, topic=private4.topic)

        utils.login(self)
        response = self.client.get(reverse('spirit:private-created-list'))
        self.assertQuerysetEqual(response.context['topics'], map(repr, [private.topic, ]))

    def test_private_created_list_order_topics(self):
        """
        private topic created list ordered by last active
        """
        private_a = utils.create_private_topic(user=self.user)
        private_b = utils.create_private_topic(user=self.user)
        private_c = utils.create_private_topic(user=self.user)
        private_a.delete()
        private_b.delete()
        private_c.delete()

        Topic.objects.filter(pk=private_a.topic.pk).update(last_active=timezone.now() - datetime.timedelta(days=10))
        Topic.objects.filter(pk=private_c.topic.pk).update(last_active=timezone.now() - datetime.timedelta(days=5))

        utils.login(self)
        response = self.client.get(reverse('spirit:private-created-list'))
        self.assertQuerysetEqual(response.context['topics'], map(repr, [private_b.topic, private_c.topic,
                                                                        private_a.topic]))


class TopicPrivateFormTest(TestCase):

    fixtures = ['spirit_init.json', ]

    def setUp(self):
        cache.clear()
        self.user = utils.create_user()
        self.user2 = utils.create_user()

    def test_private_publish(self):
        """
        create simple topic
        """
        form_data = {'title': 'foo', }
        form = TopicForPrivateForm(data=form_data)
        self.assertEqual(form.is_valid(), True)

    def test_private_create_many(self):
        """
        create many private topics accesses
        """
        users = '%s, %s' % (self.user.username, self.user2.username)
        form_data = {'users': users, }
        form = TopicPrivateManyForm(self.user, data=form_data)
        self.assertEqual(form.is_valid(), True)

        category = Category.objects.get(pk=settings.ST_TOPIC_PRIVATE_CATEGORY_PK)
        topic = utils.create_topic(category=category, user=self.user)
        form.topic = topic
        privates_saved = form.save_m2m()
        privates = TopicPrivate.objects.all()
        self.assertItemsEqual(map(repr, privates_saved), map(repr, privates))

    def test_private_create(self):
        """
        create single private topic access
        """
        category = Category.objects.get(pk=settings.ST_TOPIC_PRIVATE_CATEGORY_PK)
        topic = utils.create_topic(category=category, user=self.user)
        form_data = {'user': self.user.username, }
        form = TopicPrivateInviteForm(data=form_data)
        form.topic = topic
        self.assertEqual(form.is_valid(), True)

    def test_private_join(self):
        """
        re-join private topic if user is the creator
        """
        private = utils.create_private_topic(user=self.user)
        private.delete()

        form_data = {}
        form = TopicPrivateJoinForm(user=self.user, topic=private.topic, data=form_data)
        self.assertTrue(form.is_valid())
        private_topic = form.save()
        self.assertEqual(repr(private_topic.topic), repr(private.topic))
        self.assertEqual(repr(private_topic.user), repr(private.user))

        # topic private exists
        private = utils.create_private_topic(user=self.user)
        form = TopicPrivateJoinForm(user=self.user, topic=private.topic, data=form_data)
        self.assertFalse(form.is_valid())


class TopicTemplateTagsTest(TestCase):

    fixtures = ['spirit_init.json', ]

    def setUp(self):
        cache.clear()
        self.user = utils.create_user()
        self.category = Category.objects.get(pk=settings.ST_TOPIC_PRIVATE_CATEGORY_PK)
        self.topic = utils.create_topic(category=self.category, user=self.user)

    def test_render_invite_form(self):
        """
        display invite form
        """
        out = Template(
            "{% load spirit_tags %}"
            "{% render_invite_form topic %}"
        ).render(Context({'topic': self.topic, }))
        self.assertNotEqual(out, "")
        context = render_invite_form(self.topic)
        self.assertEqual(context['next'], None)
        self.assertIsInstance(context['form'], TopicPrivateInviteForm)
        self.assertEqual(repr(context['topic']), repr(self.topic))