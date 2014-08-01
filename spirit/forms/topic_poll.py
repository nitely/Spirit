#-*- coding: utf-8 -*-

from django import forms
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from django.utils.translation import ugettext_lazy as _

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
            raise forms.ValidationError(_("This must be greater than zero"))

        return choice_limit

    def save(self, commit=True):
        if not self.instance.pk:
            self.instance.topic = self.topic

        return super(TopicPollForm, self).save(commit)


class TopicPollChoiceInlineFormSet(BaseInlineFormSet):

    def is_filled(self):
        for form in self.forms:
            description = form.cleaned_data.get('description')
            is_marked_as_delete = form.cleaned_data.get('DELETE', False)

            if description and not is_marked_as_delete:
                return True

        return False


# TODO: use min_num and validate_min in Django 1.7
TopicPollChoiceFormSet = inlineformset_factory(TopicPoll, TopicPollChoice,
                                               formset=TopicPollChoiceInlineFormSet, fields=('description', ),
                                               extra=2, max_num=20, validate_max=True)


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

        if poll.choice_limit > 1:
            self.fields['choices'] = forms.ModelMultipleChoiceField(queryset=choices,
                                                                    widget=forms.CheckboxSelectMultiple,
                                                                    label=_("Poll choices"))
        else:
            self.fields['choices'] = forms.ModelChoiceField(queryset=choices,
                                                            empty_label=None,
                                                            widget=forms.RadioSelect,
                                                            label=_("Poll choices"))

    def load_initial(self):
        selected_choices = TopicPollChoice.objects.filter(poll=self.poll, votes__user=self.user)

        if self.poll.choice_limit == 1:
            try:
                selected_choices = selected_choices[0]
            except IndexError:
                selected_choices = None

        self.initial = {'choices': selected_choices, }

    def clean_choices(self):
        choices = self.cleaned_data['choices']

        if self.poll.choice_limit > 1:
            if len(choices) > self.poll.choice_limit:
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

        if self.poll.choice_limit == 1:
            choices = [choices, ]

        TopicPollVote.objects.filter(user=self.user, choice__poll=self.poll)\
            .delete()

        return TopicPollVote.objects.bulk_create([TopicPollVote(user=self.user, choice=choice)
                                                 for choice in choices])