# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.test import TestCase, RequestFactory
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.template import Template, Context

from ...core.tests import utils
from .models import CommentPoll, CommentPollChoice, CommentPollVote
from .forms import PollVoteManyForm
from . import tags

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
        self.poll = CommentPoll.objects.create(comment=self.comment, name='foo')
        self.poll_multi = CommentPoll.objects.create(comment=self.comment, name='bar', choice_max=2)

    def test_poll_close_logged_in(self):
        """
        User must be logged in
        """
        response = self.client.post(reverse('spirit:comment:poll:close', kwargs={'pk': self.poll.pk, }),
                                    {})
        self.assertEqual(response.status_code, 302)

    def test_poll_close_wrong_user(self):
        """
        Try to close another user poll should return 404
        """
        utils.login(self)
        response = self.client.post(reverse('spirit:comment:poll:close', kwargs={'pk': self.poll.pk, }),
                                    {})
        self.assertEqual(response.status_code, 404)

    def test_poll_close_get(self):
        """
        GET, poll_close
        """
        utils.login(self)
        response = self.client.get(reverse('spirit:comment:poll:close', kwargs={'pk': self.poll.pk, }))
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
        response = self.client.post(reverse('spirit:comment:poll:vote', kwargs={'pk': self.poll.pk, }),
                                    {})
        expected_url = reverse('spirit:user:auth:login') + "?next=" + self.poll.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302)

    def test_poll_vote_get(self):
        """
        GET, poll_vote
        Post is required
        """
        utils.login(self)
        response = self.client.get(reverse('spirit:comment:poll:vote', kwargs={'pk': self.poll.pk, }))
        self.assertEqual(response.status_code, 405)

    def test_poll_vote_post(self):
        """
        POST, poll_vote
        """
        utils.login(self)
        choice = CommentPollChoice.objects.create(poll=self.poll, number=1, description="op1")
        form_data = {'choices': choice.pk, }
        response = self.client.post(reverse('spirit:comment:poll:vote', kwargs={'pk': self.poll.pk, }),
                                    form_data)
        expected_url = self.poll.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302, target_status_code=302)
        self.assertEqual(len(CommentPollVote.objects.filter(choice=choice)), 1)

    def test_poll_vote_post_invalid(self):
        """
        POST, poll_vote
        """
        utils.login(self)
        response = self.client.post(reverse('spirit:comment:poll:vote', kwargs={'pk': self.poll.pk, }),
                                    {}, follow=True)
        self.assertEqual(len(response.context['messages']), 1)  # error message

    def test_poll_vote_post_invalid_redirect(self):
        """
        POST, poll_vote
        """
        utils.login(self)
        response = self.client.post(reverse('spirit:comment:poll:vote', kwargs={'pk': self.poll.pk, }),
                                    {})
        expected_url = self.poll.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302, target_status_code=302)

    def test_poll_vote_post_multi(self):
        """
        Should be able to vote many options
        """
        utils.login(self)
        choice_a = CommentPollChoice.objects.create(poll=self.poll_multi, number=1, description="op a")
        choice_b = CommentPollChoice.objects.create(poll=self.poll_multi, number=2, description="op b")
        CommentPollChoice.objects.create(poll=self.poll_multi, number=3, description="op c")

        form_data = {'choices': [choice_a.pk, choice_b.pk]}
        response = self.client.post(reverse('spirit:comment:poll:vote', kwargs={'pk': self.poll_multi.pk, }),
                                    form_data)
        expected_url = self.poll.get_absolute_url()

        self.assertRedirects(response, expected_url, status_code=302, target_status_code=302)
        self.assertEqual(len(CommentPollVote.objects.all()), 2)
        self.assertEqual(len(CommentPollVote.objects.filter(pk=choice_a.pk)), 1)
        self.assertEqual(len(CommentPollVote.objects.filter(pk=choice_b.pk)), 1)

    def test_poll_vote_post_count(self):
        """
        Should increase the vote counters
        """
        utils.login(self)
        choice_a = CommentPollChoice.objects.create(poll=self.poll_multi, number=1, description="op a")
        choice_b = CommentPollChoice.objects.create(poll=self.poll_multi, number=2, description="op b")
        choice_c = CommentPollChoice.objects.create(poll=self.poll_multi, number=3, description="op c")

        form_data = {'choices': [choice_a.pk, choice_b.pk]}
        response = self.client.post(
            reverse('spirit:comment:poll:vote', kwargs={'pk': self.poll_multi.pk, }), form_data
        )
        expected_url = self.poll.get_absolute_url()

        self.assertRedirects(response, expected_url, status_code=302, target_status_code=302)
        self.assertEqual(CommentPollChoice.objects.get(pk=choice_a.pk).vote_count, 1)
        self.assertEqual(CommentPollChoice.objects.get(pk=choice_b.pk).vote_count, 1)
        self.assertEqual(CommentPollChoice.objects.get(pk=choice_c.pk).vote_count, 0)

        form_data = {'choices': [choice_a.pk]}
        response = self.client.post(
            reverse('spirit:comment:poll:vote', kwargs={'pk': self.poll_multi.pk, }), form_data
        )
        expected_url = self.poll.get_absolute_url()

        self.assertRedirects(response, expected_url, status_code=302, target_status_code=302)
        self.assertEqual(CommentPollChoice.objects.get(pk=choice_a.pk).vote_count, 1)
        self.assertEqual(CommentPollChoice.objects.get(pk=choice_b.pk).vote_count, 0)
        self.assertEqual(CommentPollChoice.objects.get(pk=choice_c.pk).vote_count, 0)


class PollFormTest(TestCase):

    def setUp(self):
        cache.clear()
        self.user = utils.create_user()
        self.user2 = utils.create_user()
        self.category = utils.create_category()
        self.topic = utils.create_topic(self.category, user=self.user)
        self.comment = utils.create_comment(topic=self.topic)
        self.comment2 = utils.create_comment(topic=self.topic)

        # Single choice
        self.poll = CommentPoll.objects.create(comment=self.comment, name='foo')

        self.poll_choice = CommentPollChoice.objects.create(poll=self.poll, number=1, description="op1")
        self.poll_choice2 = CommentPollChoice.objects.create(poll=self.poll, number=2, description="op2")

        self.poll_vote = CommentPollVote.objects.create(voter=self.user, choice=self.poll_choice)
        self.poll_vote2 = CommentPollVote.objects.create(voter=self.user2, choice=self.poll_choice)

        # ...poor man prefetch
        self.poll_choice.votes = [self.poll_vote]
        self.poll.choices = [self.poll_choice, self.poll_choice2]

        # Multi choice
        self.poll_multi = CommentPoll.objects.create(comment=self.comment2, name='bar', choice_max=2)

        self.poll_multi_choice = CommentPollChoice.objects.create(poll=self.poll_multi, number=1, description="op1")
        self.poll_multi_choice2 = CommentPollChoice.objects.create(poll=self.poll_multi, number=2, description="op2")
        self.poll_multi_choice3 = CommentPollChoice.objects.create(poll=self.poll_multi, number=3, description="op3")

        self.poll_multi_vote = CommentPollVote.objects.create(voter=self.user, choice=self.poll_multi_choice)
        self.poll_multi_vote2 = CommentPollVote.objects.create(voter=self.user, choice=self.poll_multi_choice2)
        self.poll_multi_vote3 = CommentPollVote.objects.create(voter=self.user2, choice=self.poll_multi_choice)

        # ...poor man prefetch
        self.poll_multi_choice.votes = [self.poll_multi_vote]
        self.poll_multi_choice2.votes = [self.poll_multi_vote2]
        self.poll_multi.choices = [self.poll_multi_choice, self.poll_multi_choice2]

    def test_vote_load_initial_single(self):
        """
        TopicPollVoteManyForm
        """
        form = PollVoteManyForm(user=self.user, poll=self.poll)
        form.load_initial()
        self.assertEqual(form.initial, {'choices': self.poll_choice.pk, })

    def test_vote_load_initial_multi(self):
        """
        TopicPollVoteManyForm
        """
        form = PollVoteManyForm(user=self.user, poll=self.poll_multi)
        form.load_initial()
        self.assertDictEqual(form.initial, {'choices': [self.poll_multi_choice.pk, self.poll_multi_choice2.pk], })

    def test_vote_load_initial_empty(self):
        """
        TopicPollVoteManyForm
        """
        CommentPollVote.objects.all().delete()
        self.poll_choice.votes = []

        form = PollVoteManyForm(user=self.user, poll=self.poll)
        form.load_initial()
        self.assertEqual(form.initial, {})

    def test_vote_load_initial_choice_limit(self):
        """
        Load initial for a single choice poll that was previously a multi choice poll
        """
        # multi to single
        self.poll_multi.choice_max = 1

        form = PollVoteManyForm(user=self.user, poll=self.poll_multi)
        form.load_initial()
        self.assertDictEqual(form.initial, {'choices': self.poll_multi_choice.pk, })

        # single to multi
        self.poll.choice_max = 2

        form = PollVoteManyForm(user=self.user, poll=self.poll)
        form.load_initial()
        self.assertDictEqual(form.initial, {'choices': [self.poll_choice.pk, ], })

    def test_vote_poll_closed(self):
        """
        Cant vote on closed poll
        """
        self.poll.close_at = timezone.now()
        self.poll.save()

        form_data = {'choices': self.poll_choice.pk, }
        form = PollVoteManyForm(user=self.user, poll=self.poll, data=form_data)
        self.assertFalse(form.is_valid())

    def test_create_vote_single(self):
        """
        TopicPollVoteManyForm
        """
        CommentPollVote.objects.all().delete()

        form_data = {'choices': self.poll_choice.pk, }
        form = PollVoteManyForm(user=self.user, poll=self.poll, data=form_data)
        self.assertTrue(form.is_valid())
        form.save_m2m()
        self.assertEqual(len(CommentPollVote.objects.all()), 1)
        self.assertEqual(len(CommentPollVote.objects.filter(choice=self.poll_choice, is_removed=False)), 1)

    def test_create_vote_multi(self):
        """
        TopicPollVoteManyForm
        """
        CommentPollVote.objects.all().delete()
        self.poll_multi_choice.votes = []
        self.poll_multi_choice2.votes = []

        form_data = {'choices': [self.poll_multi_choice.pk, self.poll_multi_choice2.pk], }
        form = PollVoteManyForm(user=self.user, poll=self.poll_multi, data=form_data)
        self.assertTrue(form.is_valid())

    def test_create_vote_multi_invalid(self):
        """
        Limit selected choices to choice_limit
        """
        CommentPollVote.objects.all().delete()
        self.poll_multi_choice.votes = []
        self.poll_multi_choice2.votes = []

        form_data = {'choices': [self.poll_multi_choice.pk,
                                 self.poll_multi_choice2.pk,
                                 self.poll_multi_choice3.pk], }
        form = PollVoteManyForm(user=self.user, poll=self.poll_multi, data=form_data)
        self.assertFalse(form.is_valid())

    def test_update_vote_single(self):
        """
        TopicPollVoteManyForm
        """
        self.assertEqual(len(CommentPollVote.objects.filter(choice=self.poll_choice2, is_removed=False)), 0)
        self.assertEqual(len(CommentPollVote.objects.filter(choice=self.poll_choice, is_removed=False)), 2)

        form_data = {'choices': self.poll_choice2.pk, }
        form = PollVoteManyForm(user=self.user, poll=self.poll, data=form_data)
        self.assertTrue(form.is_valid())
        form.save_m2m()
        self.assertEqual(len(CommentPollVote.objects.filter(choice=self.poll_choice2, is_removed=False)), 1)
        self.assertEqual(len(CommentPollVote.objects.filter(choice=self.poll_choice, is_removed=False)), 1)


class TopicPollTemplateTagsTest(TestCase):

    def setUp(self):
        cache.clear()
        self.user = utils.create_user()
        self.category = utils.create_category()
        self.topic = utils.create_topic(category=self.category)
        self.user_comment = utils.create_comment(topic=self.topic, user=self.user, comment_html="<poll name=foo>")
        self.user_poll = CommentPoll.objects.create(comment=self.user_comment, name='foo')
        self.user_comment_with_polls = self.user_comment.__class__.objects\
            .filter(pk=self.user_comment.pk)\
            .with_polls(self.user)\
            .first()

        self.request = RequestFactory().get('/')
        self.request.user = self.user

    def test_render_polls_form(self):
        """
        Should display poll vote form
        """
        res = []

        def mock_render_to_string(tlt, ctx):
            res.append(tlt)
            res.append(ctx)

        org_render_to_string, tags.render_to_string = tags.render_to_string, mock_render_to_string
        try:
            tags.render_polls(self.user_comment_with_polls, self.request, 'csrf_token_foo')
            self.assertEqual(len(res), 2)
            template, context = res[0], res[1]
            self.assertEqual(template, 'spirit/comment/poll/_form.html')
            self.assertEqual(context['form'].poll, self.user_poll)
            self.assertIsInstance(context['poll'], CommentPoll)
            self.assertEqual(context['user'], self.user)
            self.assertEqual(context['comment'], self.user_comment_with_polls)
            self.assertEqual(context['request'], self.request)
            self.assertEqual(context['csrf_token'], 'csrf_token_foo')
        finally:
            tags.render_to_string = org_render_to_string

    def test_render_polls_template_form(self):
        """
        Should display poll vote form
        """
        out = Template(
            "{% load spirit_tags %}"
            "{% render_comment comment=comment %}"
        ).render(Context({'comment': self.user_comment_with_polls, 'request': self.request, 'csrf_token': 'foo'}))
        self.assertNotEqual(out.strip(), "")
        self.assertTrue("<poll" not in out)
        form_id = 'id="p%s"' % self.user_poll.pk
        self.assertTrue(form_id in out)
        show_link = '?show_poll=%(pk)s#p%(pk)s' % {'pk': self.user_poll.pk}
        self.assertTrue(show_link in out)

    def test_render_polls_template_form_not_author(self):
        """
        Should display poll vote form
        """
        request = RequestFactory().get('/')
        request.user = utils.create_user()
        out = Template(
            "{% load spirit_tags %}"
            "{% render_comment comment=comment %}"
        ).render(Context({'comment': self.user_comment_with_polls, 'request': request, 'csrf_token': 'foo'}))
        self.assertNotEqual(out.strip(), "")
        form_id = 'id="p%s"' % self.user_poll.pk
        self.assertTrue(form_id in out)

    def test_render_polls_template_form_close(self):
        """
        Should display the close button
        """
        out = Template(
            "{% load spirit_tags %}"
            "{% render_comment comment=comment %}"
        ).render(Context({'comment': self.user_comment_with_polls, 'request': self.request, 'csrf_token': 'foo'}))
        self.assertNotEqual(out.strip(), "")
        close_link = reverse('spirit:comment:poll:close', kwargs={'pk': self.user_poll.pk})
        self.assertTrue(close_link in out)

    def test_render_polls_template_form_close_not_author(self):
        """
        Should *not* display the close button to not poll author
        """
        request = RequestFactory().get('/')
        request.user = utils.create_user()
        out = Template(
            "{% load spirit_tags %}"
            "{% render_comment comment=comment %}"
        ).render(Context({'comment': self.user_comment_with_polls, 'request': request, 'csrf_token': 'foo'}))
        self.assertNotEqual(out.strip(), "")
        close_link = reverse('spirit:comment:poll:close', kwargs={'pk': self.user_poll.pk})
        self.assertTrue(close_link not in out)

    def test_render_polls_template_form_open(self):
        """
        Should display the open button
        """
        self.user_comment_with_polls.polls[0].close_at = timezone.now()  # renders results.html

        out = Template(
            "{% load spirit_tags %}"
            "{% render_comment comment=comment %}"
        ).render(Context({'comment': self.user_comment_with_polls, 'request': self.request, 'csrf_token': 'foo'}))
        self.assertNotEqual(out.strip(), "")
        open_link = reverse('spirit:comment:poll:open', kwargs={'pk': self.user_poll.pk})
        self.assertTrue(open_link in out)


class PollModelsTest(TestCase):

    def setUp(self):
        cache.clear()
        self.user = utils.create_user()
        self.category = utils.create_category()
        self.topic = utils.create_topic(category=self.category, user=self.user)
        self.comment = utils.create_comment(topic=self.topic)

        self.poll = CommentPoll.objects.create(comment=self.comment, name='foo')
        self.choice = CommentPollChoice.objects.create(poll=self.poll, number=1, description=1)
        self.vote = CommentPollVote.objects.create(choice=self.choice, voter=self.user)

        # Kinda like comment.with_polls()
        self.poll.choices = list(CommentPollChoice.objects.filter(poll=self.poll))

        for c in self.poll.choices:
            c.votes = list(CommentPollVote.objects.filter(choice=c, voter=self.user))

    def test_poll_is_multiple_choice(self):
        """
        Should be true when max > 1
        """
        poll = CommentPoll.objects.create(comment=self.comment, name='bar', choice_max=2)
        self.assertFalse(self.poll.is_multiple_choice)
        self.assertTrue(poll.is_multiple_choice)

    def test_poll_has_choice_min(self):
        """
        Should be true when min > 1
        """
        poll = CommentPoll.objects.create(comment=self.comment, name='bar', choice_min=2)
        self.assertFalse(self.poll.has_choice_min)
        self.assertTrue(poll.has_choice_min)

    def test_poll_is_closed(self):
        """
        Should be true when close_at > now
        """
        yesterday = timezone.now() - timezone.timedelta(days=1)
        tomorrow = timezone.now() + timezone.timedelta(days=1)
        poll_old = CommentPoll.objects.create(comment=self.comment, name='bar', close_at=yesterday)
        poll_new = CommentPoll.objects.create(comment=self.comment, name='bar2', close_at=tomorrow)
        self.assertFalse(self.poll.is_closed)
        self.assertTrue(poll_old.is_closed)
        self.assertFalse(poll_new.is_closed)

    def test_poll_has_user_voted(self):
        """
        Should be true when the user has voted
        """
        poll = CommentPoll.objects.create(comment=self.comment, name='bar')
        CommentPollChoice.objects.create(poll=poll, number=1, description=1)
        poll.choices = list(CommentPollChoice.objects.filter(poll=poll))

        for c in poll.choices:
            c.votes = []

        self.assertTrue(self.poll.has_user_voted)
        self.assertFalse(poll.has_user_voted)

    def test_poll_total_votes(self):
        """
        Should return the total votes
        """
        poll = CommentPoll.objects.create(comment=self.comment, name='bar')
        CommentPollChoice.objects.create(poll=poll, number=1, description='foo', vote_count=5)
        CommentPollChoice.objects.create(poll=poll, number=2, description='bar', vote_count=5)
        poll.choices = list(CommentPollChoice.objects.filter(poll=poll))
        self.assertEqual(poll.total_votes, 10)

    def test_poll_update_or_create_many(self):
        """
        Should create or update many polls for a given comment
        """
        pass
