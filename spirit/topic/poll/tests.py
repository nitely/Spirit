# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.template import Template, Context

from ...core.tests import utils
from .models import TopicPoll, TopicPollChoice, TopicPollVote
from .forms import TopicPollForm, TopicPollChoiceFormSet, TopicPollVoteManyForm
from .signals import topic_poll_post_vote, topic_poll_pre_vote
from .tags import render_poll_form

User = get_user_model()


class TopicPollViewTest(TestCase):

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
        response = self.client.get(reverse('spirit:topic:poll:update', kwargs={'pk': 1, }))
        self.assertEqual(response.status_code, 302)

    def test_poll_update_wrong_user(self):
        """
        Try to update another user poll should return 404
        """
        utils.login(self)
        poll = TopicPoll.objects.create(topic=self.topic2)
        response = self.client.get(reverse('spirit:topic:poll:update', kwargs={'pk': poll.pk, }))
        self.assertEqual(response.status_code, 404)

    def test_poll_update_get(self):
        """
        GET, poll_update
        """
        utils.login(self)
        poll = TopicPoll.objects.create(topic=self.topic)
        response = self.client.get(reverse('spirit:topic:poll:update', kwargs={'pk': poll.pk, }))
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
        response = self.client.post(reverse('spirit:topic:poll:update', kwargs={'pk': poll.pk, }),
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
        response = self.client.post(reverse('spirit:topic:poll:update', kwargs={'pk': poll.pk, }),
                                    form_data)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], TopicPollForm)
        self.assertIsInstance(response.context['formset'], TopicPollChoiceFormSet)

    def test_poll_close_logged_in(self):
        """
        User must be logged in
        """
        poll = TopicPoll.objects.create(topic=self.topic)
        response = self.client.get(reverse('spirit:topic:poll:close', kwargs={'pk': poll.pk, }))
        self.assertEqual(response.status_code, 302)

    def test_poll_close_wrong_user(self):
        """
        Try to close another user poll should return 404
        """
        utils.login(self)
        poll = TopicPoll.objects.create(topic=self.topic2)
        response = self.client.get(reverse('spirit:topic:poll:close', kwargs={'pk': poll.pk, }))
        self.assertEqual(response.status_code, 404)

    def test_poll_close_get(self):
        """
        GET, poll_close
        """
        utils.login(self)
        poll = TopicPoll.objects.create(topic=self.topic)
        response = self.client.get(reverse('spirit:topic:poll:close', kwargs={'pk': poll.pk, }))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['poll'].pk, poll.pk)

    def test_poll_close_post(self):
        """
        POST, poll_close
        """
        utils.login(self)
        poll = TopicPoll.objects.create(topic=self.topic)
        form_data = {}
        response = self.client.post(reverse('spirit:topic:poll:close', kwargs={'pk': poll.pk, }),
                                    form_data)
        expected_url = poll.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302)
        self.assertTrue(TopicPoll.objects.get(pk=poll.pk).is_closed)

        # Open
        response = self.client.post(reverse('spirit:topic:poll:close', kwargs={'pk': poll.pk, }),
                                    form_data)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(TopicPoll.objects.get(pk=poll.pk).is_closed)

    def test_poll_vote_logged_in(self):
        """
        User must be logged in
        """
        poll = TopicPoll.objects.create(topic=self.topic)
        form_data = {}
        response = self.client.post(reverse('spirit:topic:poll:vote', kwargs={'pk': poll.pk, }),
                                    form_data)
        expected_url = reverse('spirit:user:auth:login') + "?next=" + poll.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302)

    def test_poll_vote_get(self):
        """
        GET, poll_vote
        Post is required
        """
        utils.login(self)
        poll = TopicPoll.objects.create(topic=self.topic)
        response = self.client.get(reverse('spirit:topic:poll:vote', kwargs={'pk': poll.pk, }))
        self.assertEqual(response.status_code, 405)

    def test_poll_vote_post(self):
        """
        POST, poll_vote
        """
        utils.login(self)
        poll = TopicPoll.objects.create(topic=self.topic)
        choice = TopicPollChoice.objects.create(poll=poll, description="op1")
        form_data = {'choices': choice.pk, }
        response = self.client.post(reverse('spirit:topic:poll:vote', kwargs={'pk': poll.pk, }),
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
        response = self.client.post(reverse('spirit:topic:poll:vote', kwargs={'pk': poll.pk, }),
                                    form_data, follow=True)
        expected_url = poll.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302)
        self.assertEqual(len(response.context['messages']), 1)  # error message

    def test_poll_vote_signal(self):
        """
        POST, poll_vote
        """
        def topic_poll_pre_vote_handler(sender, poll, user, **kwargs):
            self._poll = poll
            self._user = user._wrapped
        topic_poll_pre_vote.connect(topic_poll_pre_vote_handler)

        def topic_poll_post_vote_handler(sender, poll, user, **kwargs):
            self._poll2 = poll
            self._user2 = user._wrapped
        topic_poll_post_vote.connect(topic_poll_post_vote_handler)

        utils.login(self)
        poll = TopicPoll.objects.create(topic=self.topic)
        choice = TopicPollChoice.objects.create(poll=poll, description="op1")
        form_data = {'choices': choice.pk, }
        response = self.client.post(reverse('spirit:topic:poll:vote', kwargs={'pk': poll.pk, }),
                                    form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self._poll, poll)
        self.assertEqual(self._user, self.user)
        self.assertEqual(self._poll2, poll)
        self.assertEqual(self._user2, self.user)


class TopicPollFormTest(TestCase):

    def setUp(self):
        cache.clear()
        self.user = utils.create_user()
        self.user2 = utils.create_user()
        self.category = utils.create_category()
        self.topic = utils.create_topic(self.category, user=self.user)
        self.topic2 = utils.create_topic(self.category, user=self.user2)

    def test_create_poll(self):
        """
        TopicPollForm
        """
        form_data = {'choice_limit': 1, }
        form = TopicPollForm(topic=self.topic, data=form_data)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(len(TopicPoll.objects.filter(topic=self.topic)), 1)

    def test_create_poll_invalid(self):
        """
        TopicPollForm
        """
        form_data = {'choice_limit': 0, }
        form = TopicPollForm(topic=self.topic, data=form_data)
        self.assertFalse(form.is_valid())

    def test_poll_choices_can_delete(self):
        """
        TopicPollChoiceFormSet
        """
        form = TopicPollChoiceFormSet(can_delete=True)
        self.assertIn('DELETE', [f.fields for f in form.forms][0])

        form = TopicPollChoiceFormSet(can_delete=False)
        self.assertNotIn('DELETE', [f.fields for f in form.forms][0])

    def test_create_poll_choices(self):
        """
        TopicPollChoiceFormSet
        Check it's valid and is filled
        """
        form_data = {'choices-TOTAL_FORMS': 2, 'choices-INITIAL_FORMS': 0,
                     'choices-0-description': 'op1',
                     'choices-1-description': 'op2'}
        form = TopicPollChoiceFormSet(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertTrue(form.is_filled())

    def test_create_poll_choices_unfilled(self):
        """
        TopicPollChoiceFormSet
        """
        form_data = {'choices-TOTAL_FORMS': 2, 'choices-INITIAL_FORMS': 0,
                     'choices-0-description': '',
                     'choices-1-description': ''}
        form = TopicPollChoiceFormSet(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertFalse(form.is_filled())

    def test_create_poll_choices_filled_but_deleted(self):
        """
        TopicPollChoiceFormSet, create
        """
        form_data = {'choices-TOTAL_FORMS': 2, 'choices-INITIAL_FORMS': 0,
                     'choices-0-description': 'op1', 'choices-0-DELETE': "on",
                     'choices-1-description': 'op2', 'choices-1-DELETE': "on"}
        form = TopicPollChoiceFormSet(can_delete=True, data=form_data)
        self.assertTrue(form.is_valid())  # not enough choices, but since we are NOT updating this is valid
        self.assertFalse(form.is_filled())

    def test_update_poll_choices_filled_but_deleted(self):
        """
        TopicPollChoiceFormSet, update
        is_filled should not be called when updating (coz form is always filled), but whatever
        """
        poll = TopicPoll.objects.create(topic=self.topic)
        form_data = {'choices-TOTAL_FORMS': 2, 'choices-INITIAL_FORMS': 0,
                     'choices-0-description': 'op1', 'choices-0-DELETE': "on",
                     'choices-1-description': 'op2', 'choices-1-DELETE': "on"}
        form = TopicPollChoiceFormSet(can_delete=True, data=form_data, instance=poll)
        self.assertFalse(form.is_valid())  # not enough choices
        self.assertTrue(form.is_filled())


class TopicPollVoteManyFormTest(TestCase):

    def setUp(self):
        cache.clear()
        self.user = utils.create_user()
        self.user2 = utils.create_user()
        self.category = utils.create_category()
        self.topic = utils.create_topic(self.category, user=self.user)
        self.topic2 = utils.create_topic(self.category, user=self.user2)
        self.topic3 = utils.create_topic(self.category, user=self.user2)

        self.poll = TopicPoll.objects.create(topic=self.topic, choice_limit=1)
        self.poll_multi = TopicPoll.objects.create(topic=self.topic2, choice_limit=2)

        self.poll_choice = TopicPollChoice.objects.create(poll=self.poll, description="op1")
        self.poll_choice2 = TopicPollChoice.objects.create(poll=self.poll, description="op2")

        self.poll_vote = TopicPollVote.objects.create(user=self.user, choice=self.poll_choice)
        self.poll_vote2 = TopicPollVote.objects.create(user=self.user2, choice=self.poll_choice)

        self.poll_multi_choice = TopicPollChoice.objects.create(poll=self.poll_multi, description="op1")
        self.poll_multi_choice2 = TopicPollChoice.objects.create(poll=self.poll_multi, description="op2")
        self.poll_multi_choice3 = TopicPollChoice.objects.create(poll=self.poll_multi, description="op3")

        self.poll_multi_vote = TopicPollVote.objects.create(user=self.user, choice=self.poll_multi_choice)
        self.poll_multi_vote2 = TopicPollVote.objects.create(user=self.user, choice=self.poll_multi_choice2)
        self.poll_multi_vote3 = TopicPollVote.objects.create(user=self.user2, choice=self.poll_multi_choice)

    def test_vote_load_initial_single(self):
        """
        TopicPollVoteManyForm
        """
        form = TopicPollVoteManyForm(user=self.user, poll=self.poll)
        form.load_initial()
        self.assertDictEqual(form.initial, {'choices': self.poll_choice, })

    def test_vote_load_initial_multi(self):
        """
        TopicPollVoteManyForm
        """
        form = TopicPollVoteManyForm(user=self.user, poll=self.poll_multi)
        form.load_initial()
        self.assertDictEqual(form.initial, {'choices': [self.poll_multi_choice, self.poll_multi_choice2], })

    def test_vote_load_initial_empty(self):
        """
        TopicPollVoteManyForm
        """
        TopicPollVote.objects.all().delete()

        form = TopicPollVoteManyForm(user=self.user, poll=self.poll)
        form.load_initial()
        self.assertEqual(form.initial, {})

    def test_vote_load_initial_choice_limit(self):
        """
        Load initial for a single choice poll that was previously a multi choice poll
        """
        # multi to single
        self.poll_multi.choice_limit = 1

        form = TopicPollVoteManyForm(user=self.user, poll=self.poll_multi)
        form.load_initial()
        self.assertDictEqual(form.initial, {'choices': self.poll_multi_choice, })

        # single to multi
        self.poll.choice_limit = 2

        form = TopicPollVoteManyForm(user=self.user, poll=self.poll)
        form.load_initial()
        self.assertDictEqual(form.initial, {'choices': [self.poll_choice, ], })

    def test_vote_poll_closed(self):
        """
        Cant vote on closed poll
        """
        self.poll.is_closed = True
        self.poll.save()

        form_data = {'choices': self.poll_choice.pk, }
        form = TopicPollVoteManyForm(user=self.user, poll=self.poll, data=form_data)
        self.assertFalse(form.is_valid())

    def test_create_vote_single(self):
        """
        TopicPollVoteManyForm
        """
        TopicPollVote.objects.all().delete()

        form_data = {'choices': self.poll_choice.pk, }
        form = TopicPollVoteManyForm(user=self.user, poll=self.poll, data=form_data)
        self.assertTrue(form.is_valid())
        form.save_m2m()
        self.assertEqual(len(TopicPollVote.objects.filter(choice=self.poll_choice)), 1)

    def test_create_vote_multi(self):
        """
        TopicPollVoteManyForm
        """
        TopicPollVote.objects.all().delete()

        form_data = {'choices': [self.poll_multi_choice.pk, self.poll_multi_choice2.pk], }
        form = TopicPollVoteManyForm(user=self.user, poll=self.poll_multi, data=form_data)
        self.assertTrue(form.is_valid())

    def test_create_vote_multi_invalid(self):
        """
        Limit selected choices to choice_limit
        """
        TopicPollVote.objects.all().delete()

        form_data = {'choices': [self.poll_multi_choice.pk,
                                 self.poll_multi_choice2.pk,
                                 self.poll_multi_choice3.pk], }
        form = TopicPollVoteManyForm(user=self.user, poll=self.poll_multi, data=form_data)
        self.assertFalse(form.is_valid())

    def test_update_vote_single(self):
        """
        TopicPollVoteManyForm
        """
        self.assertEqual(len(TopicPollVote.objects.filter(choice=self.poll_choice2)), 0)
        self.assertEqual(len(TopicPollVote.objects.filter(choice=self.poll_choice)), 2)

        form_data = {'choices': self.poll_choice2.pk, }
        form = TopicPollVoteManyForm(user=self.user, poll=self.poll, data=form_data)
        self.assertTrue(form.is_valid())
        form.save_m2m()
        self.assertEqual(len(TopicPollVote.objects.filter(choice=self.poll_choice2)), 1)
        self.assertEqual(len(TopicPollVote.objects.filter(choice=self.poll_choice)), 1)


class TopicPollSignalTest(TestCase):

    def setUp(self):
        cache.clear()
        self.user = utils.create_user()
        self.category = utils.create_category()
        self.topic = utils.create_topic(category=self.category, user=self.user)
        self.topic2 = utils.create_topic(category=self.category, user=self.user)

        self.poll = TopicPoll.objects.create(topic=self.topic)
        self.poll_other = TopicPoll.objects.create(topic=self.topic2)

        self.poll_choice = TopicPollChoice.objects.create(poll=self.poll, description="op1")
        self.poll_choice2 = TopicPollChoice.objects.create(poll=self.poll, description="op2")
        self.poll_other_choice = TopicPollChoice.objects.create(poll=self.poll_other, description="op2")

        self.poll_vote = TopicPollVote.objects.create(user=self.user, choice=self.poll_choice)
        self.poll_other_vote = TopicPollVote.objects.create(user=self.user, choice=self.poll_other_choice)

    def test_topic_poll_pre_vote_handler(self):
        """
        topic_poll_pre_vote_handler signal
        """
        self.poll_choice.vote_count = 2
        self.poll_choice.save()
        topic_poll_pre_vote.send(sender=self.poll.__class__, poll=self.poll, user=self.user)
        self.assertEqual(TopicPollChoice.objects.get(pk=self.poll_choice.pk).vote_count, 1)
        self.assertEqual(TopicPollChoice.objects.get(pk=self.poll_other_choice.pk).vote_count, 0)

    def test_topic_poll_post_vote_handler(self):
        """
        topic_poll_post_vote_handler signal
        """
        topic_poll_post_vote.send(sender=self.poll.__class__, poll=self.poll, user=self.user)
        self.assertEqual(TopicPollChoice.objects.get(pk=self.poll_choice.pk).vote_count, 1)
        self.assertEqual(TopicPollChoice.objects.get(pk=self.poll_other_choice.pk).vote_count, 0)


class TopicPollTemplateTagsTest(TestCase):

    def setUp(self):
        cache.clear()
        self.user = utils.create_user()
        self.category = utils.create_category()
        self.topic = utils.create_topic(category=self.category, user=self.user)

        self.poll = TopicPoll.objects.create(topic=self.topic)

    def test_render_poll_form(self):
        """
        should display poll vote form
        """
        out = Template(
            "{% load spirit_tags %}"
            "{% render_poll_form topic=topic user=user %}"
        ).render(Context({'topic': self.topic, 'user': self.user}))
        self.assertNotEqual(out.strip(), "")

        context = render_poll_form(self.topic, self.user)
        self.assertEqual(context['next'], None)
        self.assertIsInstance(context['form'], TopicPollVoteManyForm)
        self.assertEqual(context['poll'], self.poll)

    def test_render_poll_form_no_poll(self):
        """
        should display nothing
        """
        topic = utils.create_topic(category=self.category, user=self.user)

        out = Template(
            "{% load spirit_tags %}"
            "{% render_poll_form topic=topic user=user %}"
        ).render(Context({'topic': topic, 'user': self.user}))
        self.assertEqual(out.strip(), "")

    def test_render_poll_form_user(self):
        """
        should load initial or not
        """
        poll_choice = TopicPollChoice.objects.create(poll=self.poll, description="op2")
        TopicPollVote.objects.create(user=self.user, choice=poll_choice)

        self.user.is_authenticated = lambda: True
        context = render_poll_form(self.topic, self.user)
        self.assertDictEqual(context['form'].initial, {'choices': poll_choice})

        self.user.is_authenticated = lambda: False
        context = render_poll_form(self.topic, self.user)
        self.assertDictEqual(context['form'].initial, {})
