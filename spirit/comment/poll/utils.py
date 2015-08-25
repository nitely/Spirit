# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from .models import CommentPoll, CommentPollChoice


# todo: move to models

def create_polls(comment, polls_raw):
    CommentPoll.objects\
        .filter(comment=comment)\
        .update(is_removed=True)

    polls = CommentPoll.objects\
        .filter(comment=comment)

    polls_by_name = {
        poll.name: poll
        for poll in polls
    }

    for poll in polls_raw:
        instance = polls_by_name.get(poll['name'], default=CommentPoll())
        instance.name = poll['name']
        instance.is_removed = False
        instance.save()

    CommentPoll.objects\
        .filter(comment=comment, is_removed=True)\
        .delete()


def create_choices(comment, choices_raw):
    CommentPollChoice.objects\
        .filter(poll__comment=comment)\
        .update(is_removed=True)

    choices = CommentPollChoice.objects\
        .filter(poll__comment=comment)

    choices_by_number = {
        (choice.poll.name, choice.number): choice
        for choice in choices
    }

    for choice in choices_raw:
        instance = choices_by_number.get(
            (choice['poll_name'], choice['number']),
            default=CommentPollChoice()
        )
        instance.number = choice['number']
        instance.description = choice['description']
        instance.is_removed = False
        instance.save()

    CommentPollChoice.objects\
        .filter(poll__comment=comment, is_removed=True)\
        .delete()
