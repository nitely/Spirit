# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import forms
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_text
from django.core.exceptions import ValidationError

from spirit.models.topic_poll import TopicPollChoice, TopicPoll, TopicPollVote


class TopicPollForm(forms.ModelForm):

    class Meta:
        model = TopicPoll
        fields = ['choice_limit', ]

    def __init__(self, topic=None, *args, **kwargs):
        super(TopicPollForm, self).__init__(*args, **kwargs)
        self.topic = topic

    def clean_choice_limit(self):
        choice_limit = self.cleaned_data['choice_limit']

        if choice_limit < 1:
            raise forms.ValidationError(_("Choice's limit must be greater than zero"))

        return choice_limit

    def save(self, commit=True):
        if not self.instance.pk:
            self.instance.topic = self.topic

        return super(TopicPollForm, self).save(commit)


class TopicPollChoiceForm(forms.ModelForm):

    class Meta:
        model = TopicPollChoice
        fields = ['description', ]

    def is_filled(self):
        description = self.cleaned_data.get('description')
        is_marked_as_delete = self.cleaned_data.get('DELETE', False)

        if description and not is_marked_as_delete:
            return True

        return False


class TopicPollChoiceInlineFormSet(BaseInlineFormSet):

    def __init__(self, can_delete=None, *args, **kwargs):
        super(TopicPollChoiceInlineFormSet, self).__init__(*args, **kwargs)
        self._is_filled_cache = None

        if can_delete is not None:
            # Adds the *delete* checkbox or not
            self.can_delete = can_delete

    def _is_filled(self):
        if self.instance.pk:
            return True

        return any([form.is_filled() for form in self.forms])

    def is_filled(self):
        if self._is_filled_cache is None:
            self._is_filled_cache = self._is_filled()

        return self._is_filled_cache

    def has_errors(self):
        return any(self.errors) or self.non_form_errors()

    def clean(self):
        # Stores in formset.non_field_errors
        super(TopicPollChoiceInlineFormSet, self).clean()

        if not self.is_filled():
            return

        forms_filled = [form for form in self.forms if form.is_filled()]

        if len(forms_filled) < 2:
            raise ValidationError(_("There must be 2 or more choices"))

    def save(self, commit=True):
        if not self.is_filled():
            raise Exception("You should check and save if is_filled is True")

        return super(TopicPollChoiceInlineFormSet, self).save(commit=commit)


TopicPollChoiceFormSet = inlineformset_factory(TopicPollForm._meta.model, TopicPollChoiceForm._meta.model,
                                               form=TopicPollChoiceForm, formset=TopicPollChoiceInlineFormSet,
                                               max_num=20, validate_max=True, extra=2)


class TopicPollVoteManyForm(forms.Form):
    """
    This special form allows single vote and multi vote as well.
    Its beauty is that it doesn't care if the choice_limit is increased or decreased later.
    """

    def __init__(self, user=None, poll=None, *args, **kwargs):
        super(TopicPollVoteManyForm, self).__init__(*args, **kwargs)
        self.user = user
        self.poll = poll
        choices = TopicPollChoice.objects.filter(poll=poll)

        if poll.is_multiple_choice:
            self.fields['choices'] = forms.ModelMultipleChoiceField(queryset=choices,
                                                                    cache_choices=True,
                                                                    widget=forms.CheckboxSelectMultiple,
                                                                    label=_("Poll choices"))
        else:
            self.fields['choices'] = forms.ModelChoiceField(queryset=choices,
                                                            cache_choices=True,
                                                            widget=forms.RadioSelect,
                                                            label=_("Poll choices"),
                                                            empty_label=None)

        self.fields['choices'].label_from_instance = lambda obj: smart_text(obj.description)

    def load_initial(self):
        selected_choices = list(TopicPollChoice.objects.filter(poll=self.poll, votes__user=self.user))

        if not selected_choices:
            return

        if not self.poll.is_multiple_choice:
            selected_choices = selected_choices[0]

        self.initial = {'choices': selected_choices, }

    def clean_choices(self):
        choices = self.cleaned_data['choices']

        if (self.poll.is_multiple_choice and
                len(choices) > self.poll.choice_limit):
            raise forms.ValidationError(_("Too many selected choices. Limit is %s")
                                        % self.poll.choice_limit)

        return choices

    def clean(self):
        cleaned_data = super(TopicPollVoteManyForm, self).clean()

        if self.poll.is_closed:
            raise forms.ValidationError(_("This poll is closed"))

        return cleaned_data

    def save_m2m(self):
        choices = self.cleaned_data['choices']

        if not self.poll.is_multiple_choice:
            choices = [choices, ]

        TopicPollVote.objects.filter(user=self.user, choice__poll=self.poll)\
            .delete()

        return TopicPollVote.objects.bulk_create([TopicPollVote(user=self.user, choice=choice)
                                                  for choice in choices])
