# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib import messages
from django.contrib.auth.views import login as login_view, logout, password_reset
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render, get_object_or_404
from django.utils.translation import ugettext as _
from django.contrib.auth import get_user_model

from spirit.utils.ratelimit.decorators import ratelimit
from ..utils.email import send_activation_email
from ..utils.tokens import UserActivationTokenGenerator
from .forms import RegistrationForm, LoginForm, ResendActivationForm


User = get_user_model()


@ratelimit(field='username', rate='5/5m')
# TODO: @guest_only
def custom_login(request, **kwargs):
    # Currently, Django 1.5 login view does not redirect somewhere if the user is logged in
    if request.user.is_authenticated():
        return redirect(request.GET.get('next', request.user.st.get_absolute_url()))

    if request.method == "POST" and request.is_limited:
        return redirect(request.get_full_path())

    return login_view(request, authentication_form=LoginForm, **kwargs)


# TODO: @login_required ?
def custom_logout(request, **kwargs):
    # Currently, Django 1.6 uses GET to log out
    if not request.user.is_authenticated():
        return redirect(request.GET.get('next', reverse('spirit:user-login')))

    if request.method == 'POST':
        return logout(request, **kwargs)

    return render(request, 'spirit/user/auth/logout.html')


@ratelimit(field='email', rate='5/5m')
def custom_reset_password(request, **kwargs):
    if request.method == "POST" and request.is_limited:
        return redirect(reverse("spirit:password-reset"))

    return password_reset(request, **kwargs)


@ratelimit(rate='2/10s')
# TODO: @guest_only
def register(request):
    if request.user.is_authenticated():
        return redirect(request.GET.get('next', reverse('spirit:profile-update')))

    if request.method == 'POST':
        form = RegistrationForm(data=request.POST)

        if not request.is_limited and form.is_valid():
            user = form.save()
            send_activation_email(request, user)
            messages.info(request, _("We have sent you an email so you can activate your account!"))

            # TODO: email-less activation
            # if not settings.REGISTER_EMAIL_ACTIVATION_REQUIRED:
            # login(request, user)
            # return redirect(request.GET.get('next', reverse('spirit:profile-update')))

            return redirect(reverse('spirit:user-login'))
    else:
        form = RegistrationForm()

    context = {'form': form, }

    return render(request, 'spirit/user/auth/register.html', context)


def registration_activation(request, pk, token):
    user = get_object_or_404(User, pk=pk)
    activation = UserActivationTokenGenerator()

    if activation.is_valid(user, token):
        user.st.is_verified = True
        user.is_active = True
        user.save()
        messages.info(request, _("Your account has been activated!"))

    return redirect(reverse('spirit:user-login'))


@ratelimit(field='email', rate='5/5m')
# TODO: @guest_only
def resend_activation_email(request):
    if request.user.is_authenticated():
        return redirect(request.GET.get('next', reverse('spirit:profile-update')))

    if request.method == 'POST':
        form = ResendActivationForm(data=request.POST)

        if not request.is_limited and form.is_valid():
            user = form.get_user()
            send_activation_email(request, user)

        # TODO: show if is_valid only
        messages.info(request, _("If you don't receive an email, please make sure you've entered "
                                 "the address you registered with, and check your spam folder."))
        return redirect(reverse('spirit:user-login'))
    else:
        form = ResendActivationForm()

    context = {'form': form, }

    return render(request, 'spirit/user/auth/activation_resend.html', context)