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
    email_change = UserEmailChangeTokenGenerator()

    if email_change.is_valid(user, token):
        email = email_change.get_email()
        form = EmailCheckForm(data={'email': email, })

        if form.is_valid():
            user.email = form.get_email()
            user.save()
            messages.info(request, _("Your email has been changed!"))
            return redirect(reverse('spirit:profile-update'))

    messages.error(request, _("Sorry, we were not able to change your email."))
    return redirect(reverse('spirit:profile-update'))


@login_required
def topics(request, pk, slug):
    p_user = get_object_or_404(User, pk=pk)

    if p_user.st.slug != slug:
        url = reverse("spirit:profile-topics", kwargs={'pk': p_user.pk, 'slug': p_user.st.slug})
        return HttpResponsePermanentRedirect(url)

    topics = Topic.objects\
        .visible()\
        .with_bookmarks(user=request.user)\
        .filter(user=p_user)\
        .order_by('-date', '-pk')\
        .select_related('user__st')

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
def comments(request, pk, slug):
    p_user = get_object_or_404(User, pk=pk)

    if p_user.st.slug != slug:
        url = reverse("spirit:profile-detail", kwargs={'pk': p_user.pk, 'slug': p_user.st.slug})
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
def likes(request, pk, slug):
    p_user = get_object_or_404(User, pk=pk)

    if p_user.st.slug != slug:
        url = reverse("spirit:profile-likes", kwargs={'pk': p_user.pk, 'slug': p_user.st.slug})
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
def menu(request):
    return render(request, 'spirit/user/menu.html')
