# -*- coding: utf-8 -*-

import os

from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.template import defaultfilters
from django.core.files.uploadedfile import UploadedFile

from spirit.core import tasks
from spirit.core.conf import settings
from spirit.core.utils.timezone import timezones
from .models import UserProfile

User = get_user_model()
TIMEZONE_CHOICES = timezones()
Notify = UserProfile.Notify


class CleanEmailMixin:

    def clean_email(self):
        email = self.cleaned_data["email"]

        if settings.ST_CASE_INSENSITIVE_EMAILS:
            email = email.lower()

        if not settings.ST_UNIQUE_EMAILS:
            return email

        is_taken = (
            User.objects
            .filter(email=email)
            .exists())

        if is_taken:
            raise forms.ValidationError(_("The email is taken."))

        return email

    def get_email(self):
        return self.cleaned_data["email"]


class EmailCheckForm(CleanEmailMixin, forms.Form):

    email = forms.CharField(label=_("Email"), widget=forms.EmailInput, max_length=254)


class EmailChangeForm(CleanEmailMixin, forms.Form):

    email = forms.CharField(label=_("Email"), widget=forms.EmailInput, max_length=254)
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput)

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(EmailChangeForm, self).__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data["password"]

        if not self.user.check_password(password):
            raise forms.ValidationError(_("The provided password is incorrect."))

        return password


class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ("first_name", "last_name")


class AvatarWidget(forms.ClearableFileInput):
    template_name = 'spirit/user/_image_widget.html'
    clear_checkbox_label = _('Remove avatar')
    accept = ', '.join(
        '.%s' % ext
        for ext in sorted(settings.ST_ALLOWED_AVATAR_FORMAT))


class UserProfileForm(forms.ModelForm):

    timezone = forms.ChoiceField(
        label=_("Time zone"), choices=TIMEZONE_CHOICES)
    notify_when = forms.TypedChoiceField(
        label=_("Email notifications"), coerce=int, choices=Notify.WHEN)
    notify_mentions = forms.BooleanField(
        label=_("Email mentions"), required=False)
    notify_replies = forms.BooleanField(
        label=_("Email replies"), required=False)

    class Meta:
        model = UserProfile
        fields = ("avatar", "location", "timezone")
        widgets = {'avatar': AvatarWidget(attrs={'accept': AvatarWidget.accept})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        now = timezone.localtime(timezone.now())
        self.fields['timezone'].help_text = _('Current time is: %(date)s %(time)s') % {
            'date': defaultfilters.date(now),
            'time': defaultfilters.time(now)}
        self.fields['notify_when'].initial = self.instance.notify_when
        self.fields['notify_mentions'].initial = bool(
             self.instance.notify & Notify.MENTION)
        self.fields['notify_replies'].initial = bool(
            self.instance.notify & Notify.REPLY)

    def clean_avatar(self):
        file = self.cleaned_data['avatar']
        # can be bool (clear) or not an image (empty)
        if not isinstance(file, UploadedFile):
            return file

        ext = os.path.splitext(file.name)[1].lstrip('.').lower()
        if (ext not in settings.ST_ALLOWED_AVATAR_FORMAT or
                file.image.format.lower() not in settings.ST_ALLOWED_AVATAR_FORMAT):
            raise forms.ValidationError(
                _("Unsupported file format. Supported formats are %s.") %
                ", ".join(settings.ST_ALLOWED_AVATAR_FORMAT))

        return file

    def clean_notify_mentions(self):
        if self.cleaned_data['notify_mentions']:
            return Notify.MENTION
        return 0

    def clean_notify_replies(self):
        if self.cleaned_data['notify_replies']:
            return Notify.REPLY
        return 0

    def save(self, *args, **kwargs):
        self.instance.notify = (
            self.cleaned_data['notify_when'] |
            self.cleaned_data['notify_mentions'] |
            self.cleaned_data['notify_replies'])
        instance = super().save(*args, **kwargs)
        if isinstance(self.cleaned_data['avatar'], UploadedFile):
            tasks.make_avatars(self.instance.user_id)
        return instance
