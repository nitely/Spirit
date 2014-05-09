#-*- coding: utf-8 -*-

import json
import datetime

from django.test import TestCase, TransactionTestCase, RequestFactory
from django.test.utils import override_settings
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.conf import settings
from django.template import Template, Context
from django.utils import timezone

import utils

from spirit.models.topic_private import TopicPrivate

from spirit.models.topic_notification import TopicNotification, comment_posted, \
    COMMENT, MENTION, topic_private_post_create, topic_private_access_pre_create, topic_viewed
from spirit.forms.topic_notification import NotificationCreationForm, NotificationForm
from spirit.templatetags.tags.topic_notification import render_notification_form, has_topic_notifications


@override_settings(ST_NOTIFICATIONS_PER_PAGE=1)
class TopicNotificationViewTest(TestCase):

    fixtures = ['spirit_init.json', ]

    def setUp(self):
        cache.clear()
        self.user = utils.create_user()
        self.user2 = utils.create_user()
        self.category = utils.create_category()
        self.topic = utils.create_topic(self.category)
        self.comment = utils.create_comment(topic=self.topic)

        # comment notification
        self.topic_notification = TopicNotification.objects.create(user=self.user, topic=self.topic,
                                                                   comment=self.comment, is_active=True,
                                                                   action=COMMENT)
        self.topic_notification2 = TopicNotification.objects.create(user=self.user2, topic=self.topic,
                                                                    comment=self.comment, is_active=True,
                                                                    action=COMMENT)

        # subscription to topic
        self.topic2 = utils.create_topic(self.category)
        self.topic_subscrption = TopicNotification.objects.create(user=self.user, topic=self.topic2, is_active=True)

    def test_topic_notification_list(self):
        """
        topic notification list
        """
        utils.login(self)
        response = self.client.get(reverse('spirit:topic-notification-list'))
        self.assertQuerysetEqual(response.context['notifications'], map(repr, [self.topic_notification, ]))

    def test_topic_notification_list_show_private_topic(self):
        """
        topic private in notification list
        """
        TopicNotification.objects.all().delete()

        topic_a = utils.create_private_topic(user=self.user)
        topic_notif = TopicNotification.objects.create(user=self.user, topic=topic_a.topic,
                                                       comment=self.comment, is_active=True, action=COMMENT)

        utils.login(self)
        response = self.client.get(reverse('spirit:topic-notification-list'))
        self.assertQuerysetEqual(response.context['notifications'], map(repr, [topic_notif, ]))

        # list unread should behave the same
        response = self.client.get(reverse('spirit:topic-notification-list-unread'))
        self.assertQuerysetEqual(response.context['page'], map(repr, [topic_notif, ]))

        # ajax list should behave the same
        response = self.client.get(reverse('spirit:topic-notification-ajax'),
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        res = json.loads(response.content)
        self.assertEqual(len(res['n']), 1)

    def test_topic_notification_list_dont_show_topic_removed_or_no_access(self):
        """
        dont show private topics if user has no access or is removed
        """
        TopicNotification.objects.all().delete()

        category = utils.create_category()
        category_removed = utils.create_category(is_removed=True)
        subcategory = utils.create_category(parent=category_removed)
        subcategory_removed = utils.create_category(parent=category, is_removed=True)
        topic_a = utils.create_private_topic()
        topic_b = utils.create_topic(category=category, is_removed=True)
        topic_c = utils.create_topic(category=category_removed)
        topic_d = utils.create_topic(category=subcategory)
        topic_e = utils.create_topic(category=subcategory_removed)
        unread_a = TopicNotification.objects.create(user=self.user, topic=topic_a.topic,
                                                    comment=self.comment, is_active=True, action=COMMENT)
        unread_b = TopicNotification.objects.create(user=self.user, topic=topic_b,
                                                    comment=self.comment, is_active=True, action=COMMENT)
        unread_c = TopicNotification.objects.create(user=self.user, topic=topic_c,
                                                    comment=self.comment, is_active=True, action=COMMENT)
        unread_d = TopicNotification.objects.create(user=self.user, topic=topic_d,
                                                    comment=self.comment, is_active=True, action=COMMENT)
        unread_e = TopicNotification.objects.create(user=self.user, topic=topic_e,
                                                    comment=self.comment, is_active=True, action=COMMENT)
        self.assertEqual(len(TopicNotification.objects.filter(user=self.user, is_active=True, is_read=False)), 5)

        utils.login(self)
        response = self.client.get(reverse('spirit:topic-notification-list'))
        self.assertQuerysetEqual(response.context['notifications'], [])

        # list unread should behave the same
        response = self.client.get(reverse('spirit:topic-notification-list-unread'))
        self.assertQuerysetEqual(response.context['page'], [])

        # ajax list should behave the same
        response = self.client.get(reverse('spirit:topic-notification-ajax'),
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        res = json.loads(response.content)
        self.assertEqual(len(res['n']), 0)

    @override_settings(ST_NOTIFICATIONS_PER_PAGE=10)
    def test_topic_notification_list_unread(self):
        """
        topic notification list
        """
        topic = utils.create_topic(self.category, user=self.user2)
        comment = utils.create_comment(topic=topic, user=self.user2)
        topic_notification = TopicNotification.objects.create(user=self.user, topic=topic,
                                                              comment=comment, is_active=True,
                                                              action=COMMENT)

        utils.login(self)
        response = self.client.get(reverse('spirit:topic-notification-list-unread'))
        self.assertQuerysetEqual(response.context['page'], map(repr, [topic_notification, self.topic_notification]))

        # fake next page
        response = self.client.get(reverse('spirit:topic-notification-list-unread') + "?notif=" + str(topic_notification.pk))
        self.assertQuerysetEqual(response.context['page'], map(repr, [self.topic_notification, ]))

    def test_topic_notification_ajax(self):
        """
        get notifications
        """
        utils.login(self)
        response = self.client.get(reverse('spirit:topic-notification-ajax'),
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        res = json.loads(response.content)
        self.assertEqual(len(res['n']), 1)
        expected = {
            'user': self.topic_notification.comment.user.username,
            'action': self.topic_notification.text_action,
            'title': self.topic_notification.comment.topic.title,
            'url': self.topic_notification.get_absolute_url(),
            'is_read': self.topic_notification.is_read
        }
        self.assertItemsEqual(res['n'][0], expected)
        self.assertFalse(TopicNotification.objects.get(pk=self.topic_notification.pk).is_read)

    def test_topic_notification_ajax_limit(self):
        """
        get first N notifications
        """
        user = utils.create_user()
        topic = utils.create_topic(self.category, user=user)
        comment = utils.create_comment(topic=topic, user=user)
        TopicNotification.objects.create(user=self.user, topic=topic, comment=comment,
                                         is_active=True, action=COMMENT)

        utils.login(self)
        response = self.client.get(reverse('spirit:topic-notification-ajax'),
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        res = json.loads(response.content)
        self.assertGreater(TopicNotification.objects.filter(user=self.user), 1)
        self.assertEqual(len(res['n']), 1)

    @override_settings(ST_NOTIFICATIONS_PER_PAGE=20)
    def test_topic_notification_ajax_order(self):
        """
        order by is_read=False first then by date
        """
        user = utils.create_user()

        for _ in xrange(10):
            topic = utils.create_topic(self.category, user=user)
            comment = utils.create_comment(topic=topic, user=user)
            TopicNotification.objects.create(user=self.user, topic=topic, comment=comment,
                                             is_active=True, action=COMMENT)

        TopicNotification.objects.filter(user=self.user).update(is_read=True)
        old_date = timezone.now() - datetime.timedelta(days=10)
        TopicNotification.objects.filter(pk=self.topic_notification.pk).update(is_read=False, date=old_date)

        utils.login(self)
        response = self.client.get(reverse('spirit:topic-notification-ajax'),
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        res = json.loads(response.content)
        self.assertFalse(res['n'][0]['is_read'])
        self.assertTrue(res['n'][1]['is_read'])

    def test_topic_notification_create(self):
        """
        create notification
        """
        TopicNotification.objects.all().delete()

        utils.login(self)
        form_data = {'is_active': True, }
        response = self.client.post(reverse('spirit:topic-notification-create', kwargs={'topic_id': self.topic.pk, }),
                                    form_data)
        self.assertRedirects(response, self.topic.get_absolute_url(), status_code=302)
        self.assertEqual(len(TopicNotification.objects.all()), 1)

    def test_topic_notification_create_has_access(self):
        """
        create notification for private topic if user has access
        """
        TopicNotification.objects.all().delete()
        private = utils.create_private_topic(user=self.user)

        utils.login(self)
        form_data = {'is_active': True, }
        response = self.client.post(reverse('spirit:topic-notification-create', kwargs={'topic_id': private.topic.pk, }),
                                    form_data)
        self.assertRedirects(response, private.topic.get_absolute_url(), status_code=302)
        self.assertEqual(len(TopicNotification.objects.all()), 1)

    def test_topic_notification_create_no_access(self):
        """
        raise Http404 if topic is private and user has no access
        """
        private = utils.create_private_topic()

        utils.login(self)
        form_data = {'is_active': True, }
        response = self.client.post(reverse('spirit:topic-notification-create', kwargs={'topic_id': private.topic.pk, }),
                                    form_data)
        self.assertEqual(response.status_code, 404)

    def test_topic_notification_update(self):
        """
        update notification
        """
        utils.login(self)
        form_data = {'is_active': True, }
        response = self.client.post(reverse('spirit:topic-notification-update',
                                            kwargs={'pk': self.topic_notification.pk, }),
                                    form_data)
        self.assertRedirects(response, self.topic.get_absolute_url(), status_code=302)
        notification = TopicNotification.objects.get(pk=self.topic_notification.pk)
        self.assertEqual(notification.action, COMMENT)

    def test_topic_notification_update_invalid_user(self):
        """
        test user cant unsubscribe other user
        """
        user = utils.create_user()
        notification = TopicNotification.objects.create(user=user, topic=self.topic)

        utils.login(self)
        form_data = {}
        response = self.client.post(reverse('spirit:topic-notification-update', kwargs={'pk': notification.pk, }),
                                    form_data)
        self.assertEqual(response.status_code, 404)


class TopicNotificationFormTest(TestCase):

    fixtures = ['spirit_init.json', ]

    def setUp(self):
        cache.clear()
        self.user = utils.create_user()

    def test_notification_creation(self):
        """
        create notification
        """
        category = utils.create_category()
        topic = utils.create_topic(category)
        form_data = {'is_active': True, }
        form = NotificationCreationForm(data=form_data)
        form.user = self.user
        form.topic = topic
        self.assertEqual(form.is_valid(), True)

        TopicNotification.objects.create(user=self.user, topic=topic,
                                         is_active=True, action=COMMENT)
        form = NotificationCreationForm(data=form_data)
        form.user = self.user
        form.topic = topic
        self.assertEqual(form.is_valid(), False)

    def test_notification(self):
        """
        update notification
        """
        category = utils.create_category()
        topic = utils.create_topic(category)
        notification = TopicNotification.objects.create(user=self.user, topic=topic,
                                                        is_active=True, action=COMMENT)

        form_data = {'is_active': True, }
        form = NotificationForm(data=form_data, instance=notification)
        self.assertEqual(form.is_valid(), True)


class TopicNotificationSignalTest(TransactionTestCase):

    fixtures = ['spirit_init.json', ]

    def setUp(self):
        cache.clear()
        self.user = utils.create_user()
        self.user2 = utils.create_user()
        self.category = utils.create_category()
        self.topic = utils.create_topic(self.category)
        self.comment = utils.create_comment(topic=self.topic)
        self.topic_notification = TopicNotification.objects.create(user=self.user, topic=self.topic,
                                                                   comment=self.comment, is_active=True,
                                                                   action=COMMENT, is_read=True)
        self.topic_notification2 = TopicNotification.objects.create(user=self.user2, topic=self.topic,
                                                                    comment=self.comment, is_active=True,
                                                                    action=COMMENT, is_read=True)

    def test_topic_notification_comment_handler(self):
        """
        set is_read=False when a comment is posted
        """
        comment = utils.create_comment(topic=self.topic)
        comment_posted.send(sender=self.topic.__class__, comment=comment, mentions=None)
        self.assertFalse(TopicNotification.objects.get(pk=self.topic_notification.pk).is_read)

    def test_topic_notification_comment_handler_unactive(self):
        """
        do nothing if notification is_active=False
        """
        TopicNotification.objects.filter(pk=self.topic_notification.pk).update(is_active=False)
        comment = utils.create_comment(topic=self.topic_notification.topic)
        comment_posted.send(sender=self.topic.__class__, comment=comment, mentions=None)
        self.assertTrue(TopicNotification.objects.get(pk=self.topic_notification.pk).is_read)

    def test_topic_notification_mention_handler(self):
        """
        create notification on mention
        """
        topic = utils.create_topic(self.category)
        mentions = {self.user.username: self.user, }
        comment = utils.create_comment(topic=topic)
        comment_posted.send(sender=self.topic.__class__, comment=comment, mentions=mentions)
        self.assertEqual(TopicNotification.objects.get(user=self.user, comment=comment).action, MENTION)
        self.assertFalse(TopicNotification.objects.get(user=self.user, comment=comment).is_read)

    def test_topic_notification_mention_handler_unactive(self):
        """
        set is_read=False when user gets mentioned
        even if is_active=False
        """
        TopicNotification.objects.filter(pk=self.topic_notification.pk).update(is_active=False)
        mentions = {self.user.username: self.user, }
        comment = utils.create_comment(topic=self.topic_notification.topic)
        comment_posted.send(sender=self.topic.__class__, comment=comment, mentions=mentions)
        self.assertEqual(TopicNotification.objects.get(pk=self.topic_notification.pk).action, MENTION)
        self.assertFalse(TopicNotification.objects.get(pk=self.topic_notification.pk).is_read)

    def test_topic_private_post_create_handler(self):
        """
        create notifications on topic private created
        """
        private = utils.create_private_topic()
        private2 = TopicPrivate.objects.create(user=self.user, topic=private.topic)
        comment = utils.create_comment(topic=private.topic)
        topic_private_post_create.send(sender=private.__class__,
                                       topics_private=[private, private2],
                                       comment=comment)
        self.assertEqual(len(TopicNotification.objects.filter(user=private.user, topic=private.topic)), 0)
        notification = TopicNotification.objects.get(user=private2.user, topic=private2.topic)
        self.assertTrue(notification.is_active)
        self.assertFalse(notification.is_read)
        self.assertEqual(repr(notification.comment), repr(comment))

    def test_topic_private_access_pre_create_handler(self):
        """
        create notifications on topic private access created
        """
        private = utils.create_private_topic()
        comment = utils.create_comment(topic=private.topic)
        topic_private_access_pre_create.send(sender=private.__class__,
                                             topic=private.topic,
                                             user=private.user)
        notification = TopicNotification.objects.get(user=private.user, topic=private.topic)
        self.assertEqual(notification.action, COMMENT)
        self.assertTrue(notification.is_active)
        self.assertFalse(notification.is_read)
        self.assertEqual(repr(notification.comment), repr(comment))

        # creating the access again should do nothing
        topic_private_access_pre_create.send(sender=private.__class__,
                                             topic=private.topic,
                                             user=private.user)

    def test_topic_viewed_handler(self):
        """
        mark notification as read when the user visits the topic
        """
        req = RequestFactory().get('/')
        req.user = self.user
        private = utils.create_private_topic()
        TopicNotification.objects.create(user=private.user, topic=private.topic, is_read=False)
        topic_viewed.send(sender=private.__class__,
                          topic=private.topic,
                          request=req)
        notification = TopicNotification.objects.get(user=private.user, topic=private.topic)
        self.assertFalse(notification.is_read)


class TopicNotificationTemplateTagsTest(TestCase):

    fixtures = ['spirit_init.json', ]

    def setUp(self):
        cache.clear()
        self.user = utils.create_user()
        self.category = utils.create_category()
        self.topic = utils.create_topic(self.category)
        self.comment = utils.create_comment(topic=self.topic)

        self.topic_notification = TopicNotification.objects.create(user=self.user, topic=self.topic,
                                                                   comment=self.comment, is_active=True,
                                                                   action=COMMENT)

    def test_get_topic_notifications_has_notifications(self):
        """
        should tell if there are new notifications
        """
        template = Template(
            "{% load spirit_tags %}"
            "{% has_topic_notifications user=user as has_notifications %}"
            "{{ has_notifications }}"
        )
        context = Context({'user': self.user, })

        out = template.render(context)
        self.assertEqual(out, "True")

        TopicNotification.objects.all().update(is_read=True)
        out = template.render(context)
        self.assertEqual(out, "False")

    def test_topic_notification_has_notifications_dont_count_topic_removed_or_no_access(self):
        """
        dont show private topics if user has no access or is removed
        """
        TopicNotification.objects.all().delete()

        category = utils.create_category()
        category_removed = utils.create_category(is_removed=True)
        subcategory = utils.create_category(parent=category_removed)
        subcategory_removed = utils.create_category(parent=category, is_removed=True)
        topic_a = utils.create_private_topic()
        topic_b = utils.create_topic(category=category, is_removed=True)
        topic_c = utils.create_topic(category=category_removed)
        topic_d = utils.create_topic(category=subcategory)
        topic_e = utils.create_topic(category=subcategory_removed)
        unread_a = TopicNotification.objects.create(user=self.user, topic=topic_a.topic,
                                                    comment=self.comment, is_active=True, action=COMMENT)
        unread_b = TopicNotification.objects.create(user=self.user, topic=topic_b,
                                                    comment=self.comment, is_active=True, action=COMMENT)
        unread_c = TopicNotification.objects.create(user=self.user, topic=topic_c,
                                                    comment=self.comment, is_active=True, action=COMMENT)
        unread_d = TopicNotification.objects.create(user=self.user, topic=topic_d,
                                                    comment=self.comment, is_active=True, action=COMMENT)
        unread_e = TopicNotification.objects.create(user=self.user, topic=topic_e,
                                                    comment=self.comment, is_active=True, action=COMMENT)

        self.assertEqual(len(TopicNotification.objects.filter(user=self.user, is_active=True, is_read=False)), 5)
        self.assertFalse(has_topic_notifications(self.user))

    def test_render_notification_form_notify(self):
        """
        should display the form
        """
        out = Template(
            "{% load spirit_tags %}"
            "{% render_notification_form user topic %}"
        ).render(Context({'topic': self.topic, 'user': self.user}))

        # unnotify
        context = render_notification_form(self.user, self.topic)
        self.assertIsNone(context['next'])
        self.assertIsInstance(context['form'], NotificationForm)
        self.assertEqual(context['topic_id'], self.topic.pk)
        self.assertEqual(context['notification'], self.topic_notification)

        # notify
        topic2 = utils.create_topic(self.category)
        context = render_notification_form(self.user, topic2)
        self.assertIsNone(context['notification'])