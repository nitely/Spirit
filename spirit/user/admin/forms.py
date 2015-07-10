# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import forms
from django.contrib.auth import get_user_model

from ..models import UserProfile

User = get_user_model()


class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ("username", "email", "is_active")


class UserProfileForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        fields = ("location", "timezone", "is_administrator", "is_moderator")