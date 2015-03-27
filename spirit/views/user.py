# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.views import login as login_view
from django.contrib.auth.views import password_reset, logout
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.http import HttpResponsePermanentRedirect

from djconfig import config

from ..utils.ratelimit.decorators import ratelimit
from ..utils.user.email import send_activation_email, send_email_change_email
from ..utils.user.tokens import UserActivationTokenGenerator, UserEmailChangeTokenGenerator
from ..utils.paginator import yt_paginate

from ..models.topic import Topic
from ..models.comment import Comment

from ..forms.user import UserProfileForm, RegistrationForm, LoginForm, EmailChangeForm, ResendActivationForm


User = get_user_model()


@ratelimit(field='username', rate='5/5m')
# TODO: @guest_only
def custom_login(request, **kwargs):
    # Current Django 1.5 login view does not redirect somewhere if the user is logged in
    if request.user.is_authenticated():
        return redirect(request.GET.get('next', request.user.get_absolute_url()))

    if request.is_limited and request.method == "POST":
        return redirect(request.get_full_path())

    return login_view(request, authentication_form=LoginForm, **kwargs)


# TODO: @login_required ?
def custom_logout(request, **kwargs):
    # Current Django 1.6 uses GET to log out
    if not request.user.is_authenticated():
        return redirect(request.GET.get('next', reverse('spirit:user-login')))

    if request.method == 'POST':
        return logout(request, **kwargs)

    return render(request, 'spirit/user/logout.html')


@ratelimit(field='email', rate='5/5m')
def custom_reset_password(request, **kwargs):
    if request.is_limited and request.method == "POST":
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

    return render(request, 'spirit/user/register.html', context)


def registration_activation(request, pk, token):
    user = get_object_or_404(User, pk=pk)
    activation = UserActivationTokenGenerator()

    if activation.is_valid(user, token):
        user.is_verified = True
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

    return render(request, 'spirit/user/activation_resend.html', context)


@login_required
def profile_update(request):
    if request.method == 'POST':
        form = UserProfileForm(data=request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            messages.info(request, _("Your profile has been updated!"))
            return redirect(reverse('spirit:profile-update'))
    else:
        form = UserProfileForm(instance=request.user)

    context = {'form': form, }

    return render(request, 'spirit/user/profile_update.html', context)


@login_required
def profile_password_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)

        if form.is_valid():
            form.save()
            messages.info(request, _("Your password has been changed!"))
            return redirect(reverse('spirit:profile-update'))
    else:
        form = PasswordChangeForm(user=request.user)

    context = {'form': form, }

    return render(request, 'spirit/user/profile_password_change.html', context)


@login_required
def profile_email_change(request):
    if request.method == 'POST':
        form = EmailChangeForm(user=request.user, data=request.POST)

        if form.is_valid():
            send_email_change_email(request, request.user, form.get_email())
            messages.info(request, _("We have sent you an email so you can confirm the change!"))
            return redirect(reverse('spirit:profile-update'))
    else:
        form = EmailChangeForm()

    context = {'form': form, }

    return render(request, 'spirit/user/profile_email_change.html', context)


@login_required
def email_change_confirm(request, token):
    user = request.user
    email_change = UserEmailChangeTokenGenerator()

    if email_change.is_valid(user, token):
        user.email = email_change.get_email()
        user.save()
        messages.info(request, _("Your email has been changed!"))

    return redirect(reverse('spirit:profile-update'))


@login_required
def profile_topics(request, pk, slug):
    p_user = get_object_or_404(User, pk=pk)

    if p_user.slug != slug:
        url = reverse("spirit:profile-topics", kwargs={'pk': p_user.pk, 'slug': p_user.slug})
        return HttpResponsePermanentRedirect(url)

    topics = Topic.objects\
        .visible()\
        .with_bookmarks(user=request.user)\
        .filter(user=p_user)\
        .order_by('-date', '-pk')\
        .select_related('user')

    topics = yt_paginate(
        topics,
        per_page=config.topics_per_page,
        page_number=request.GET.get('page', 1)
    )

    context = {
        'p_user': p_user,
        'topics': topics
    }

    return render(request, 'spirit/user/profile_topics.html', context)


@login_required
def profile_comments(request, pk, slug):
    p_user = get_object_or_404(User, pk=pk)

    if p_user.slug != slug:
        url = reverse("spirit:profile-detail", kwargs={'pk': p_user.pk, 'slug': p_user.slug})
        return HttpResponsePermanentRedirect(url)

    comments = Comment.objects\
        .visible()\
        .filter(user=p_user)

    comments = yt_paginate(
        comments,
        per_page=config.comments_per_page,
        page_number=request.GET.get('page', 1)
    )

    context = {
        'p_user': p_user,
        'comments': comments
    }

    return render(request, 'spirit/user/profile_comments.html', context)


@login_required
def profile_likes(request, pk, slug):
    p_user = get_object_or_404(User, pk=pk)

    if p_user.slug != slug:
        url = reverse("spirit:profile-likes", kwargs={'pk': p_user.pk, 'slug': p_user.slug})
        return HttpResponsePermanentRedirect(url)

    comments = Comment.objects\
        .visible()\
        .filter(comment_likes__user=p_user)\
        .order_by('-comment_likes__date', '-pk')

    comments = yt_paginate(
        comments,
        per_page=config.comments_per_page,
        page_number=request.GET.get('page', 1)
    )

    context = {
        'p_user': p_user,
        'comments': comments
    }

    return render(request, 'spirit/user/profile_likes.html', context)


@login_required
def user_menu(request):
    return render(request, 'spirit/user/menu.html')
