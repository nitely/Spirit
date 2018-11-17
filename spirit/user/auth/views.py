# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib import messages
from django.contrib.auth import views as django_views
from django.urls import reverse
from django.shortcuts import redirect, render, get_object_or_404
from django.utils.translation import ugettext as _
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy

from ...core.utils.ratelimit.decorators import ratelimit
from ..utils.email import send_activation_email
from ..utils.tokens import UserActivationTokenGenerator
from .forms import RegistrationForm, LoginForm, ResendActivationForm

User = get_user_model()


# I wish django would not force its crappy CBV on us
class _CustomPasswordResetView(django_views.PasswordResetView):
    template_name = 'spirit/user/auth/password_reset_form.html'
    email_template_name = 'spirit/user/auth/password_reset_email.html'
    subject_template_name = 'spirit/user/auth/password_reset_subject.txt'
    success_url = reverse_lazy('spirit:user:auth:password-reset-done')


class _CustomPasswordResetConfirmView(django_views.PasswordResetConfirmView):
    template_name = 'spirit/user/auth/password_reset_confirm.html'
    success_url = reverse_lazy('spirit:user:auth:password-reset-complete')


class _CustomPasswordResetCompleteView(django_views.PasswordResetCompleteView):
    template_name = 'spirit/user/auth/password_reset_complete.html'


class _CustomPasswordResetDoneView(django_views.PasswordResetDoneView):
    template_name = 'spirit/user/auth/password_reset_done.html'


class _CustomLoginView(django_views.LoginView):
    template_name = 'spirit/user/auth/login.html'


# Make views sane again
_login_view = _CustomLoginView.as_view()
_logout_view = django_views.LogoutView.as_view()
_password_reset_view = _CustomPasswordResetView.as_view()
custom_password_reset_confirm = _CustomPasswordResetConfirmView.as_view()
custom_password_reset_complete = _CustomPasswordResetCompleteView.as_view()
custom_password_reset_done = _CustomPasswordResetDoneView.as_view()


@ratelimit(field='username', rate='5/5m')
# TODO: @guest_only
def custom_login(request, **kwargs):
    # Currently, Django 1.5 login view does not redirect somewhere if the user is logged in
    if request.user.is_authenticated:
        return redirect(request.GET.get('next', request.user.st.get_absolute_url()))

    if request.method == "POST" and request.is_limited():
        return redirect(request.get_full_path())

    return _login_view(request, authentication_form=LoginForm, **kwargs)


# TODO: @login_required ?
def custom_logout(request, **kwargs):
    if not request.user.is_authenticated:
        return redirect(request.GET.get('next', reverse('spirit:user:auth:login')))

    if request.method == 'POST':
        return _logout_view(request, **kwargs)

    return render(request, 'spirit/user/auth/logout.html')


@ratelimit(field='email', rate='5/5m')
def custom_password_reset(request, **kwargs):
    if request.method == "POST" and request.is_limited():
        return redirect(reverse("spirit:user:auth:password-reset"))

    return _password_reset_view(request, **kwargs)


@ratelimit(rate='2/10s')
# TODO: @guest_only
def register(request, registration_form=RegistrationForm):
    if request.user.is_authenticated:
        return redirect(request.GET.get('next', reverse('spirit:user:update')))

    if request.method == 'POST':
        form = registration_form(data=request.POST)

        if not request.is_limited() and form.is_valid():
            user = form.save()
            send_activation_email(request, user)
            messages.info(
                request, _(
                    "We have sent you an email to %(email)s "
                    "so you can activate your account!") % {'email': form.get_email()})

            # TODO: email-less activation
            # if not settings.REGISTER_EMAIL_ACTIVATION_REQUIRED:
            # login(request, user)
            # return redirect(request.GET.get('next', reverse('spirit:user:update')))

            return redirect(reverse('spirit:user:auth:login'))
    else:
        form = registration_form()

    context = {'form': form}

    return render(request, 'spirit/user/auth/register.html', context)


def registration_activation(request, pk, token):
    user = get_object_or_404(User, pk=pk)
    activation = UserActivationTokenGenerator()

    if activation.is_valid(user, token):
        user.st.is_verified = True
        user.is_active = True
        user.save()
        messages.info(request, _("Your account has been activated!"))

    return redirect(reverse('spirit:user:auth:login'))


@ratelimit(field='email', rate='5/5m')
# TODO: @guest_only
def resend_activation_email(request):
    if request.user.is_authenticated:
        return redirect(request.GET.get('next', reverse('spirit:user:update')))

    if request.method == 'POST':
        form = ResendActivationForm(data=request.POST)

        if not request.is_limited() and form.is_valid():
            user = form.get_user()
            send_activation_email(request, user)

        # TODO: show if is_valid only
        messages.info(
            request, _(
                "If you don't receive an email, please make sure you've entered "
                "the address you registered with, and check your spam folder."))
        return redirect(reverse('spirit:user:auth:login'))
    else:
        form = ResendActivationForm()

    context = {'form': form}

    return render(request, 'spirit/user/auth/activation_resend.html', context)
