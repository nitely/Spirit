# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.utils import timezone

from ...core.tests import utils
from .models import CommentPoll, CommentPollChoice, CommentPollVote

User = get_user_model()


class PollViewTest(TestCase):

    def setUp(self):
        cache.clear()
        self.user = utils.create_user()
        self.user2 = utils.create_user()
        self.category = utils.create_category()
        self.topic = utils.create_topic(self.category, user=self.user)
        self.topic2 = utils.create_topic(self.category, user=self.user2)
        self.comment = utils.create_comment(topic=self.topic)
        self.user_comment = utils.create_comment(topic=self.topic, user=self.user)

    def test_poll_close_logged_in(self):
        """
        User must be logged in
        """
        poll = CommentPoll.objects.create(comment=self.comment, name='foo')
        response = self.client.post(reverse('spirit:comment:poll:close', kwargs={'pk': poll.pk, }),
                                    {})
        self.assertEqual(response.status_code, 302)

    def test_poll_close_wrong_user(self):
        """
        Try to close another user poll should return 404
        """
        utils.login(self)
        poll = CommentPoll.objects.create(comment=self.comment, name='foo')
        response = self.client.post(reverse('spirit:comment:poll:close', kwargs={'pk': poll.pk, }),
                                    {})
        self.assertEqual(response.status_code, 404)

    def test_poll_close_get(self):
        """
        GET, poll_close
        """
        utils.login(self)
        poll = CommentPoll.objects.create(comment=self.comment, name='foo')
        response = self.client.get(reverse('spirit:comment:poll:close', kwargs={'pk': poll.pk, }))
        self.assertEqual(response.status_code, 405)

    def test_poll_close_post(self):
        """
        POST, poll_close
        """
        utils.login(self)
        poll = CommentPoll.objects.create(comment=self.user_comment, name='foo')
        response = self.client.post(reverse('spirit:comment:poll:close', kwargs={'pk': poll.pk, }),
                                    {})
        expected_url = poll.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302, target_status_code=302)
        self.assertTrue(CommentPoll.objects.get(pk=poll.pk).is_closed)

    def test_poll_close_open_post(self):
        """
        POST, poll_open
        """
        utils.login(self)
        poll = CommentPoll.objects.create(comment=self.user_comment, name='foo', close_at=timezone.now())
        self.assertTrue(poll.is_closed)
        response = self.client.post(reverse('spirit:comment:poll:open', kwargs={'pk': poll.pk, }),
                                    {})
        expected_url = poll.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302, target_status_code=302)
        self.assertFalse(CommentPoll.objects.get(pk=poll.pk).is_closed)

    def test_poll_vote_logged_in(self):
        """
        User must be logged in
        """
        poll = CommentPoll.objects.create(comment=self.comment, name='foo')
        response = self.client.post(reverse('spirit:comment:poll:vote', kwargs={'pk': poll.pk, }),
                                    {})
        expected_url = reverse('spirit:user:auth:login') + "?next=" + poll.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302)

    def test_poll_vote_get(self):
        """
        GET, poll_vote
        Post is required
        """
        utils.login(self)
        poll = CommentPoll.objects.create(comment=self.comment, name='foo')
        response = self.client.get(reverse('spirit:comment:poll:vote', kwargs={'pk': poll.pk, }))
        self.assertEqual(response.status_code, 405)

    def test_poll_vote_post(self):
        """
        POST, poll_vote
        """
        utils.login(self)
        poll = CommentPoll.objects.create(comment=self.comment, name='foo')
        choice = CommentPollChoice.objects.create(poll=poll, number=1, description="op1")
        form_data = {'choices': choice.pk, }
        response = self.client.post(reverse('spirit:comment:poll:vote', kwargs={'pk': poll.pk, }),
                                    form_data)
        expected_url = poll.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302, target_status_code=302)
        self.assertEqual(len(CommentPollVote.objects.filter(choice=choice)), 1)

    def test_poll_vote_post_invalid(self):
        """
        POST, poll_vote
        """
        utils.login(self)
        poll = CommentPoll.objects.create(comment=self.comment, name='foo')
        response = self.client.post(reverse('spirit:comment:poll:vote', kwargs={'pk': poll.pk, }),
                                    {}, follow=True)
        self.assertEqual(len(response.context['messages']), 1)  # error message

    def test_poll_vote_post_invalid_redirect(self):
        """
        POST, poll_vote
        """
        utils.login(self)
        poll = CommentPoll.objects.create(comment=self.comment, name='foo')
        response = self.client.post(reverse('spirit:comment:poll:vote', kwargs={'pk': poll.pk, }),
                                    {})
        expected_url = poll.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302, target_status_code=302)
