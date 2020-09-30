# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.utils.encoding import smart_bytes

from ...core.conf import settings
from ...core import utils
from ...core.utils.widgets import (
    MultipleInput,
    CIMultipleInput,
    CITextInput)
from ...topic.models import Topic
from ...category.models import Category
from .models import TopicPrivate

User = get_user_model()


class TopicForPrivateForm(forms.ModelForm):

    topic_hash = forms.CharField(
        max_length=32,
        widget=forms.HiddenInput,
        required=False)

    class Meta:
        model = Topic
        fields = ('title', )

    def __init__(self, user=None, *args, **kwargs):
        super(TopicForPrivateForm, self).__init__(*args, **kwargs)
        self.user = user
        self._category = None

    @property
    def category(self):
        if self._category:
            return self._category

        self._category = Category.objects.get(
            pk=settings.ST_TOPIC_PRIVATE_CATEGORY_PK)

        return self._category

    def get_topic_hash(self):
        topic_hash = self.cleaned_data.get('topic_hash', None)

        if topic_hash:
            return topic_hash

        return utils.get_hash((
            smart_bytes(self.cleaned_data['title']),
            smart_bytes('category-{}'.format(self.category.pk))))

    def save(self, commit=True):
        if not self.instance.pk:
            self.instance.user = self.user
            self.instance.category = self.category

        return super(TopicForPrivateForm, self).save(commit)


def cx_multiple_input(*args, **kwargs):
    if settings.ST_CASE_INSENSITIVE_USERNAMES:
        return CIMultipleInput(*args, **kwargs)
    return MultipleInput(*args, **kwargs)


class TopicPrivateManyForm(forms.Form):

    # Only good for create
    users = forms.ModelMultipleChoiceField(
        label=_("Invite users"),
        queryset=User.objects.all(),
        to_field_name=User.USERNAME_FIELD)

    def __init__(self, user=None, topic=None, *args, **kwargs):
        super(TopicPrivateManyForm, self).__init__(*args, **kwargs)
        self.user = user
        self.topic = topic
        # Make it dynamic for testing
        self.fields['users'].widget = cx_multiple_input(
            attrs={'placeholder': _("user1, user2, ...")})

    def clean_users(self):
        users = set(self.cleaned_data['users'])

        if self.user not in users:
            users.add(self.user)

        return users

    def get_users(self):
        users = set(self.cleaned_data['users'])
        users.remove(self.user)
        return users

    def save_m2m(self):
        users = self.cleaned_data['users']
        # Since the topic was just created this should not raise an exception
        return TopicPrivate.objects.bulk_create(
            [TopicPrivate(user=user, topic=self.topic)
             for user in users])


def cx_text_input(*args, **kwargs):
    if settings.ST_CASE_INSENSITIVE_USERNAMES:
        return CITextInput(*args, **kwargs)
    return forms.TextInput(*args, **kwargs)


class TopicPrivateInviteForm(forms.ModelForm):

    # Only good for create
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        to_field_name=User.USERNAME_FIELD,
        label=_("Invite user"))

    def __init__(self, topic=None, *args, **kwargs):
        super(TopicPrivateInviteForm, self).__init__(*args, **kwargs)
        self.topic = topic
        # Make it dynamic for testing
        self.fields['user'].widget = cx_text_input(
            attrs={'placeholder': _("username")})

    class Meta:
        model = TopicPrivate
        fields = ("user", )

    def clean_user(self):
        user = self.cleaned_data['user']

        private = TopicPrivate.objects.filter(
            user=user, topic=self.topic)

        if private.exists():
            # Do this since some of the unique_together fields are excluded.
            raise forms.ValidationError(
                _("%(username)s is already a participant") %
                {'username': user.st.nickname})

        return user

    def get_user(self):
        return self.cleaned_data['user']

    def save(self, commit=True):
        if not self.instance.pk:
            self.instance.topic = self.topic

        return super(TopicPrivateInviteForm, self).save(commit)


class TopicPrivateJoinForm(forms.ModelForm):

    def __init__(self, topic=None, user=None, *args, **kwargs):
        super(TopicPrivateJoinForm, self).__init__(*args, **kwargs)
        self.topic = topic
        self.user = user

    class Meta:
        model = TopicPrivate
        fields = ()

    def clean(self):
        cleaned_data = super(TopicPrivateJoinForm, self).clean()

        private = TopicPrivate.objects.filter(
            user=self.user, topic=self.topic)

        if private.exists():
            # Do this since some of the unique_together fields are excluded.
            raise forms.ValidationError(
                _("%(username)s is already a participant") %
                {'username': self.user.st.nickname})

        return cleaned_data

    def get_user(self):
        return self.user

    def save(self, commit=True):
        if not self.instance.pk:
            self.instance.topic = self.topic
            self.instance.user = self.user

        return super(TopicPrivateJoinForm, self).save(commit)
