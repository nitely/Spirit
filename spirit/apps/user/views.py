# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.http import HttpResponsePermanentRedirect
from djconfig import config

from spirit.utils.paginator import yt_paginate
from .utils.email import send_email_change_email
from .utils.tokens import UserEmailChangeTokenGenerator
from ..topic.models import Topic
from ..comment.models import Comment
from .forms import UserProfileForm, EmailChangeForm, UserForm, EmailCheckForm


User = get_user_model()


@login_required
def update(request):
    if request.method == 'POST':
        uform = UserForm(data=request.POST, instance=request.user)
        form = UserProfileForm(data=request.POST, instance=request.user.st)

        if all([uform.is_valid(), form.is_valid()]):  # TODO: test!
            uform.save()
            form.save()
            messages.info(request, _("Your profile has been updated!"))
            return redirect(reverse('spirit:profile-update'))
    else:
        uform = UserForm(instance=request.user)
        form = UserProfileForm(instance=request.user.st)

    context = {
        'form': form,
        'uform': uform
    }

    return render(request, 'spirit/user/profile_update.html', context)


@login_required
def password_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)

        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.info(request, _("Your password has been changed!"))
            return redirect(reverse('spirit:profile-update'))
    else:
        form = PasswordChangeForm(user=request.user)

    context = {'form': form, }

    return render(request, 'spirit/user/profile_password_change.html', context)


@login_required
def email_change(request):
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
    user_email_change = UserEmailChangeTokenGenerator()

    if user_email_change.is_valid(user, token):
        email = user_email_change.get_email()
        form = EmailCheckForm(data={'email': email, })

        if form.is_valid():
            user.email = form.get_email()
            user.save()
            messages.info(request, _("Your email has been changed!"))
            return redirect(reverse('spirit:profile-update'))

    messages.error(request, _("Sorry, we were not able to change your email."))
    return redirect(reverse('spirit:profile-update'))


@login_required
def _lists(request, pk, slug, queryset, template, reverse_to, context_name, per_page):
    p_user = get_object_or_404(User, pk=pk)

    if p_user.st.slug != slug:
        url = reverse(reverse_to, kwargs={'pk': p_user.pk, 'slug': p_user.st.slug})
        return HttpResponsePermanentRedirect(url)

    items = yt_paginate(
        queryset,
        per_page=per_page,
        page_number=request.GET.get('page', 1)
    )

    context = {
        'p_user': p_user,
        context_name: items
    }

    return render(request, template, context)


def topics(request, pk, slug):
    user_topics = Topic.objects\
        .visible()\
        .with_bookmarks(user=request.user)\
        .filter(user_id=pk)\
        .order_by('-date', '-pk')\
        .select_related('user__st')

    return _lists(
        request, pk, slug,
        queryset=user_topics,
        template='spirit/user/profile_topics.html',
        reverse_to='spirit:profile-topics',
        context_name='topics',
        per_page=config.topics_per_page
    )


def comments(request, pk, slug):
    user_comments = Comment.objects\
        .visible()\
        .filter(user_id=pk)

    return _lists(
        request, pk, slug,
        queryset=user_comments,
        template='spirit/user/profile_comments.html',
        reverse_to='spirit:profile-detail',
        context_name='comments',
        per_page=config.comments_per_page,
    )


def likes(request, pk, slug):
    user_comments = Comment.objects\
        .visible()\
        .filter(comment_likes__user_id=pk)\
        .order_by('-comment_likes__date', '-pk')

    return _lists(
        request, pk, slug,
        queryset=user_comments,
        template='spirit/user/profile_likes.html',
        reverse_to='spirit:profile-likes',
        context_name='comments',
        per_page=config.comments_per_page,
    )


@login_required
def menu(request):
    return render(request, 'spirit/user/menu.html')
