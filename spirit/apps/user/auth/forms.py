# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import ugettext_lazy as _

from ..forms import EmailUniqueMixin


User = get_user_model()


class RegistrationForm(EmailUniqueMixin, UserCreationForm):

    honeypot = forms.CharField(label=_("Leave blank"), required=False)

    class Meta:
        model = User
        fields = ("username", "email")

    def clean_honeypot(self):
        """Check that nothing has been entered into the honeypot."""
        value = self.cleaned_data["honeypot"]

        if value:
            raise forms.ValidationError(_("Do not fill this field."))

        return value

    def clean_username(self):
        username = self.cleaned_data["username"]

        is_taken = User._default_manager\
            .filter(username=username)\
            .exists()

        if is_taken:
            raise forms.ValidationError(_("The username is taken."))

        return username

    def save(self, commit=True):
        self.instance.is_active = False
        return super(RegistrationForm, self).save(commit)


class LoginForm(AuthenticationForm):

    username = forms.CharField(label=_("Username or Email"), max_length=254)


class ResendActivationForm(forms.Form):

    email = forms.CharField(label=_("Email"), widget=forms.EmailInput)

    def clean_email(self):
        email = self.cleaned_data["email"]

        try:
            self.user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise forms.ValidationError(_("The provided email does not exists."))
        except User.MultipleObjectsReturned:
            # TODO: refactor!
            users = User.objects\
                .filter(email=email, st__is_verified=False)\
                .order_by('-pk')

            users = users[:1]  # Limit to the first found.

            if not len(users):
                raise forms.ValidationError(_("This account is verified, try logging-in."))

            self.user = users[0]

        if self.user.st.is_verified:
            raise forms.ValidationError(_("This account is verified, try logging-in."))

        return email

    def get_user(self):
        return self.user