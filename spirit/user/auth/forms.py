from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from spirit.core import tasks
from spirit.core.conf import settings
from spirit.user.forms import CleanEmailMixin

User = get_user_model()


class RegistrationForm(CleanEmailMixin, forms.ModelForm):
    email2 = forms.CharField(
        label=_("Email confirmation"),
        widget=forms.EmailInput,
        max_length=254,
        help_text=_("Enter the same email as above, for verification."),
    )
    # todo: add password validator for Django 1.9
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    honeypot = forms.CharField(label=_("Leave blank"), required=False)

    class Meta:
        model = User
        fields = ("username", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].required = True  # Django model does not requires it

    def clean_honeypot(self):
        """Check that nothing has been entered into the honeypot."""
        value = self.cleaned_data["honeypot"]

        if value:
            raise forms.ValidationError(_("Do not fill this field."))

        return value

    def clean_username(self):
        username = self.cleaned_data["username"]

        if settings.ST_CASE_INSENSITIVE_USERNAMES:
            username = username.lower()

        is_taken = User.objects.filter(username=username).exists()
        if is_taken:
            raise forms.ValidationError(_("The username is taken."))

        return self.cleaned_data["username"]

    def clean_email2(self):
        email = self.cleaned_data.get("email")
        email2 = self.cleaned_data["email2"]

        if settings.ST_CASE_INSENSITIVE_EMAILS:
            email2 = email2.lower()

        if email and email != email2:
            raise forms.ValidationError(_("The two email fields didn't match."))

        return email2

    def save(self, commit=True):
        self.instance.is_active = False
        self.instance.set_password(self.cleaned_data["password"])
        return super().save(commit)


class LoginForm(AuthenticationForm):
    username = forms.CharField(label=_("Username or Email"), max_length=254)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_messages["invalid_login"] = _("The password is not valid.")

    def _validate_username(self):
        """
        Check the username exists.\
        Show if the username or email is invalid\
        instead of the unclear "username or\
        password is invalid" message.
        """
        username = self.cleaned_data.get("username")

        if not username:
            return

        if settings.ST_CASE_INSENSITIVE_USERNAMES:
            username = username.lower()

        is_found = User.objects.filter(username=username).exists()
        if is_found:
            return

        if settings.ST_CASE_INSENSITIVE_EMAILS:
            username = username.lower()

        is_found_email = User.objects.filter(email=username).exists()
        if is_found_email:
            return

        raise forms.ValidationError(
            _("No account matches %(username)s.") % {"username": username}
        )

    def clean(self):
        self._validate_username()
        return super().clean()


class ResendActivationForm(forms.Form):
    email = forms.CharField(label=_("Email"), widget=forms.EmailInput, max_length=254)

    def clean_email(self):
        email = self.cleaned_data["email"]

        if settings.ST_CASE_INSENSITIVE_EMAILS:
            email = email.lower()

        is_existent = User.objects.filter(email=email).exists()
        if not is_existent:
            raise forms.ValidationError(_("The provided email does not exists."))

        self.user = (
            User.objects.filter(email=email, st__is_verified=False)
            .order_by("-pk")
            .first()
        )
        if not self.user:
            raise forms.ValidationError(_("This account is verified, try logging-in."))

        return email

    def get_user(self):
        return self.user


class CustomPasswordResetForm(PasswordResetForm):
    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    ):
        subject = render_to_string(subject_template_name, context)
        subject = "".join(subject.splitlines())
        body = render_to_string(email_template_name, context)
        tasks.send_email(subject, body, [to_email])
