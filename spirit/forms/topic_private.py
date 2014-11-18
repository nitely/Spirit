# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.conf import settings

from ..models.topic import Topic
from ..models.category import Category

from ..utils.widgets import MultipleInput
from ..models.topic_private import TopicPrivate


User = get_user_model()


class TopicForPrivateForm(forms.ModelForm):

    class Meta:
        model = Topic
        fields = ('title', )

    def __init__(self, user=None, *args, **kwargs):
        super(TopicForPrivateForm, self).__init__(*args, **kwargs)
        self.user = user

    def save(self, commit=True):
        if not self.instance.pk:
            self.instance.user = self.user
            self.instance.category = Category.objects.get(pk=settings.ST_TOPIC_PRIVATE_CATEGORY_PK)

        return super(TopicForPrivateForm, self).save(commit)


class TopicPrivateManyForm(forms.Form):

    # Only good for create
    users = forms.ModelMultipleChoiceField(queryset=User.objects.all(),
                                           to_field_name=User.USERNAME_FIELD,
                                           widget=MultipleInput(attrs={'placeholder': _("user1, user2, ..."), }))

    def __init__(self, user=None, topic=None, *args, **kwargs):
        super(TopicPrivateManyForm, self).__init__(*args, **kwargs)
        self.user = user
        self.topic = topic

    def clean_users(self):
        users = set(self.cleaned_data['users'])

        if self.user not in users:
            users.add(self.user)

        return users

    def save_m2m(self):
        users = self.cleaned_data['users']
        # Since the topic was just created this should not raise an exception
        return TopicPrivate.objects.bulk_create([TopicPrivate(user=user, topic=self.topic)
                                                 for user in users])


class TopicPrivateInviteForm(forms.ModelForm):

    # Only good for create
    user = forms.ModelChoiceField(queryset=User.objects.all(),
                                  to_field_name=User.USERNAME_FIELD,
                                  widget=forms.TextInput(attrs={'placeholder': _("username"), }),
                                  label=_("Invite user"))

    def __init__(self, topic=None, *args, **kwargs):
        super(TopicPrivateInviteForm, self).__init__(*args, **kwargs)
        self.topic = topic

    class Meta:
        model = TopicPrivate
        fields = ("user", )

    def clean_user(self):
        user = self.cleaned_data['user']

        private = TopicPrivate.objects.filter(user=user,
                                              topic=self.topic)

        if private.exists():
            # Do this since some of the unique_together fields are excluded.
            raise forms.ValidationError(_("%(username)s is already a participant") %
                                        {'username': getattr(user, user.USERNAME_FIELD), })

        return user

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

        private = TopicPrivate.objects.filter(user=self.user,
                                              topic=self.topic)

        if private.exists():
            # Do this since some of the unique_together fields are excluded.
            raise forms.ValidationError(_("%(username)s is already a participant") %
                                        {'username': getattr(self.user, self.user.USERNAME_FIELD), })

        return cleaned_data

    def save(self, commit=True):
        if not self.instance.pk:
            self.instance.topic = self.topic
            self.instance.user = self.user

        return super(TopicPrivateJoinForm, self).save(commit)
