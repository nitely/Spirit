#-*- coding: utf-8 -*-

from django.test import TestCase, RequestFactory
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User as UserModel
from django.contrib.auth import get_user_model

import utils

from spirit.models.topic_poll import TopicPoll, TopicPollChoice, TopicPollVote
from spirit.forms.topic_poll import TopicPollForm, TopicPollChoiceFormSet


User = get_user_model()


class TopicPollViewTest(TestCase):

    fixtures = ['spirit_init.json', ]

    def setUp(self):
        cache.clear()
        self.user = utils.create_user()
        self.user2 = utils.create_user()
        self.category = utils.create_category()
        self.topic = utils.create_topic(self.category, user=self.user)
        self.topic2 = utils.create_topic(self.category, user=self.user2)

    def test_poll_update_logged_in(self):
        """
        User must be logged in
        """
        response = self.client.get(reverse('spirit:poll-update', kwargs={'pk': 1, }))
        self.assertEqual(response.status_code, 302)

    def test_poll_update_wrong_user(self):
        """
        Try to update another user poll should return 404
        """
        utils.login(self)
        poll = TopicPoll.objects.create(topic=self.topic2)
        response = self.client.get(reverse('spirit:poll-update', kwargs={'pk': poll.pk, }))
        self.assertEqual(response.status_code, 404)

    def test_poll_update_get(self):
        """
        GET, poll_update
        """
        utils.login(self)
        poll = TopicPoll.objects.create(topic=self.topic)
        response = self.client.get(reverse('spirit:poll-update', kwargs={'pk': poll.pk, }))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], TopicPollForm)
        self.assertIsInstance(response.context['formset'], TopicPollChoiceFormSet)

    def test_poll_update_post(self):
        """
        POST, poll_update
        """
        utils.login(self)
        poll = TopicPoll.objects.create(topic=self.topic)
        form_data = {'choices-TOTAL_FORMS': 2, 'choices-INITIAL_FORMS': 0,
                     'choices-0-description': 'op1', 'choices-0-poll': poll.pk,
                     'choices-1-description': 'op2', 'choices-1-poll': poll.pk,
                     'choice_limit': 2}
        response = self.client.post(reverse('spirit:poll-update', kwargs={'pk': poll.pk, }),
                                    form_data)
        expected_url = poll.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302)
        self.assertEqual(TopicPoll.objects.get(pk=poll.pk).choice_limit, 2)
        self.assertEqual(len(TopicPollChoice.objects.filter(poll=poll.pk)), 2)

    def test_poll_update_post_invalid(self):
        """
        POST, poll_update
        """
        utils.login(self)
        poll = TopicPoll.objects.create(topic=self.topic)
        form_data = {'choices-TOTAL_FORMS': 2, 'choices-INITIAL_FORMS': 0}
        response = self.client.post(reverse('spirit:poll-update', kwargs={'pk': poll.pk, }),
                                    form_data)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], TopicPollForm)
        self.assertIsInstance(response.context['formset'], TopicPollChoiceFormSet)

    def test_poll_close_logged_in(self):
        """
        User must be logged in
        """
        poll = TopicPoll.objects.create(topic=self.topic)
        response = self.client.get(reverse('spirit:poll-close', kwargs={'pk': poll.pk, }))
        self.assertEqual(response.status_code, 302)

    def test_poll_close_wrong_user(self):
        """
        Try to close another user poll should return 404
        """
        utils.login(self)
        poll = TopicPoll.objects.create(topic=self.topic2)
        response = self.client.get(reverse('spirit:poll-close', kwargs={'pk': poll.pk, }))
        self.assertEqual(response.status_code, 404)

    def test_poll_close_get(self):
        """
        GET, poll_close
        """
        utils.login(self)
        poll = TopicPoll.objects.create(topic=self.topic)
        response = self.client.get(reverse('spirit:poll-close', kwargs={'pk': poll.pk, }))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['poll'].pk, poll.pk)

    def test_poll_close_post(self):
        """
        POST, poll_close
        """
        utils.login(self)
        poll = TopicPoll.objects.create(topic=self.topic)
        form_data = {}
        response = self.client.post(reverse('spirit:poll-close', kwargs={'pk': poll.pk, }),
                                    form_data)
        expected_url = poll.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302)
        self.assertTrue(TopicPoll.objects.get(pk=poll.pk).is_closed)

        # Open
        response = self.client.post(reverse('spirit:poll-close', kwargs={'pk': poll.pk, }),
                                    form_data)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(TopicPoll.objects.get(pk=poll.pk).is_closed)

    def test_poll_vote_logged_in(self):
        """
        User must be logged in
        """
        poll = TopicPoll.objects.create(topic=self.topic)
        form_data = {}
        response = self.client.post(reverse('spirit:poll-vote', kwargs={'pk': poll.pk, }),
                                    form_data)
        expected_url = reverse('spirit:user-login') + "?next=" + poll.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302)

    def test_poll_vote_get(self):
        """
        GET, poll_vote
        Post is required
        """
        utils.login(self)
        poll = TopicPoll.objects.create(topic=self.topic)
        response = self.client.get(reverse('spirit:poll-vote', kwargs={'pk': poll.pk, }))
        self.assertEqual(response.status_code, 405)

    def test_poll_vote_post(self):
        """
        POST, poll_vote
        """
        utils.login(self)
        poll = TopicPoll.objects.create(topic=self.topic)
        choice = TopicPollChoice.objects.create(poll=poll, description="op1")
        form_data = {'choices': choice.pk, }
        response = self.client.post(reverse('spirit:poll-vote', kwargs={'pk': poll.pk, }),
                                    form_data)
        expected_url = poll.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302)
        self.assertEqual(len(TopicPollVote.objects.filter(choice=choice)), 1)

    def test_poll_vote_post_invalid(self):
        """
        POST, poll_vote
        """
        utils.login(self)
        poll = TopicPoll.objects.create(topic=self.topic)
        form_data = {}
        response = self.client.post(reverse('spirit:poll-vote', kwargs={'pk': poll.pk, }),
                                    form_data, follow=True)
        expected_url = poll.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302)
        self.assertEqual(len(response.context['messages']), 1)  # error message