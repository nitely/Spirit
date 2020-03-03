# -*- coding: utf-8 -*-

import logging

import mistune

from django.utils import timezone

from spirit.comment.poll.models import CommentPoll, CommentPollChoice, PollMode


__all__ = ['PollParser']
logger = logging.getLogger('django')


class ParserError(Exception):
    """"""


class PollParser(object):

    fields = {'invalid_params', 'invalid_body', 'name', 'title',
              'min', 'max', 'close', 'choices', 'mode'}

    def __init__(self, polls, data):
        assert set(data.keys()) == self.fields

        self.data = data
        self.polls = polls
        self.close_max_len = 5  # Fixed length
        self.choices_limit = 20  # make a setting
        self.cleaned_data = {}

        self._field_name = CommentPoll._meta.get_field('name')
        self._field_title = CommentPoll._meta.get_field('title')
        self._field_description = CommentPollChoice._meta.get_field('description')

    def _pre_validation(self):
        if self.data['invalid_params'] is not None:
            raise ParserError('Invalid parameters')

        if self.data['invalid_body'] is not None:
            raise ParserError('Invalid body')

        # Avoid further processing if the choice max is reached
        if len(self.polls['choices']) >= self.choices_limit:
            raise ParserError('Choices limit has been reached')

    def _clean_poll(self):
        name_raw = self.data['name']
        title_raw = self.data['title']
        min_raw = self.data['min']
        max_raw = self.data['max']
        close_at_raw = self.data['close']
        mode_raw = self.data['mode']

        poll = {
            'name': name_raw[:self._field_name.max_length]
        }

        if title_raw:
            title = mistune.escape(title_raw.strip(), quote=True)
            poll['title'] = title[:self._field_title.max_length]  # May be empty

        if min_raw:
            poll['choice_min'] = int(min_raw)

        if max_raw:
            poll['choice_max'] = int(max_raw)

        if close_at_raw:
            days = int(close_at_raw[:self.close_max_len])
            poll['close_at'] = timezone.now() + timezone.timedelta(days=days)

        if mode_raw:
            poll['mode'] = PollMode.BY_NAME[mode_raw]

        self.cleaned_data['poll'] = poll

    def _clean_choices(self):
        choices_raw = self.data['choices']
        choices = []

        for choice in choices_raw.splitlines()[:self.choices_limit + 1]:
            number, description = choice.split('.', 1)
            description = mistune.escape(description.strip(), quote=True)
            choices.append({
                'number': int(number),
                'description': description[:self._field_description.max_length]
                # 'poll_name': ...  # Added in clean() method
            })

        self.cleaned_data['choices'] = choices

    def _clean(self):
        poll = self.cleaned_data['poll']
        choices = self.cleaned_data['choices']

        # Allow to use min without max (default max=choices_length)
        if 'choice_min' in poll and 'choice_max' not in poll:
            poll['choice_max'] = len(choices)

        name = poll['name']

        for choice in choices:
            choice['poll_name'] = name

    def _post_validation(self):
        poll = self.cleaned_data['poll']
        choices = self.cleaned_data['choices']

        # _post_validate_choices_limit()
        choices_count = len(choices) + len(self.polls['choices'])

        if choices_count > self.choices_limit:
            raise ParserError('Choices limit has been reached')

        # _post_validate_poll_name()
        name = poll['name']
        names = set(p['name'] for p in self.polls['polls'])

        if name in names:  # Is this poll name already listed?
            raise ParserError('Poll name is duplicated')

        # _post_validate_choice_numbers()
        numbers = [c['number'] for c in choices]

        if len(numbers) != len(set(numbers)):  # Non unique numbers?
            raise ParserError('Choices numbers are duplicated')

        # _post_validate_poll_min_max()
        choice_min = poll.get('choice_min')
        choice_max = poll.get('choice_max')
        has_min = choice_min is not None
        has_max = choice_max is not None

        if has_min and has_max and choice_min > choice_max:
            raise ParserError('Min can\'t be greater than max')

        if has_min and choice_min < 1:
            raise ParserError('Min can\'t be lesser than 1')

        if has_max and choice_max < 1:
            raise ParserError('Max can\'t be lesser than 1')

    def is_valid(self):
        # In the spirit of markdown
        # errors shouldn't and won't be displayed to the user
        try:
            self._pre_validation()
            self._clean_poll()
            self._clean_choices()
            self._clean()
            self._post_validation()
        except ParserError as err:
            logger.debug(err)
            return False

        return True
