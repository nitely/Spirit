# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.html import mark_safe

from .models import CommentPollVote


class PollVoteManyForm(forms.Form):
    """
    This special form allows single vote and multi vote as well.
    Its beauty is that it doesn't care if the choice_max
    is increased or decreased later.
    """

    def __init__(self, poll, user=None, *args, **kwargs):
        super(PollVoteManyForm, self).__init__(*args, **kwargs)
        self.auto_id = 'id_poll_{pk}_%s'.format(pk=poll.pk)  # Uniqueness "<label for=id_poll_pk_..."
        self.user = user
        self.poll = poll
        self.poll_choices = getattr(poll, 'choices', poll.poll_choices.unremoved())
        choices = ((c.pk, mark_safe(c.description)) for c in self.poll_choices)

        if poll.is_multiple_choice:
            self.fields['choices'] = forms.MultipleChoiceField(
                choices=choices,
                widget=forms.CheckboxSelectMultiple,
                label=_("Poll choices")
            )
        else:
            self.fields['choices'] = forms.ChoiceField(
                choices=choices,
                widget=forms.RadioSelect,
                label=_("Poll choices")
            )

    def load_initial(self):
        selected_choices = [
            c.pk
            for c in self.poll_choices
            if c.vote
        ]

        if not selected_choices:
            return

        if not self.poll.is_multiple_choice:
            selected_choices = selected_choices[0]

        self.initial = {'choices': selected_choices, }

    def clean_choices(self):
        choices = self.cleaned_data['choices']

        if not self.poll.is_multiple_choice:
            return choices

        if len(choices) > self.poll.choice_max:
            raise forms.ValidationError(
                _("Too many selected choices. Limit is %s")
                % self.poll.choice_max
            )

        if len(choices) < self.poll.choice_min:  # todo: test!
            raise forms.ValidationError(
                _("Too few selected choices. Minimum is %s")
                % self.poll.choice_min
            )

        return choices

    def clean(self):
        cleaned_data = super(PollVoteManyForm, self).clean()

        if self.poll.is_closed:
            raise forms.ValidationError(_("This poll is closed"))

        return cleaned_data

    def save_m2m(self):
        choices = self.cleaned_data['choices']

        if not self.poll.is_multiple_choice:
            choices = [choices, ]

        CommentPollVote.objects\
            .filter(voter=self.user, choice__poll=self.poll)\
            .update(is_removed=True)

        for choice_id in choices:
            CommentPollVote.objects.update_or_create(
                voter=self.user,
                choice_id=choice_id,
                defaults={'is_removed': False}
            )
