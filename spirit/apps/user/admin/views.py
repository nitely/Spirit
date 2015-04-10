# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.utils.translation import ugettext as _
from djconfig import config

from spirit.utils.paginator import yt_paginate
from spirit.utils.decorators import administrator_required
from spirit.apps.admin.forms import UserForm, UserProfileForm


User = get_user_model()


@administrator_required
def user_edit(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        uform = UserForm(data=request.POST, instance=user)
        form = UserProfileForm(data=request.POST, instance=user.st)

        if uform.is_valid() and form.is_valid():
            uform.save()
            form.save()
            messages.info(request, _("This profile has been updated!"))
            return redirect(request.GET.get("next", request.get_full_path()))
    else:
        uform = UserForm(instance=user)
        form = UserProfileForm(instance=user.st)

    context = {
        'form': form,
        'uform': uform
        }

    return render(request, 'spirit/user/admin/edit.html', context)


@administrator_required
def user_list(request):
    users = yt_paginate(
        User.objects.all().order_by('-date_joined', '-pk'),
        per_page=config.topics_per_page,
        page_number=request.GET.get('page', 1)
    )
    context = {'users': users, }
    return render(request, 'spirit/user/admin/list.html', context)


@administrator_required
def user_admins(request):
    users = yt_paginate(
        User.objects.filter(st__is_administrator=True).order_by('-date_joined', '-pk'),
        per_page=config.topics_per_page,
        page_number=request.GET.get('page', 1)
    )
    context = {'users': users, }
    return render(request, 'spirit/user/admin/admins.html', context)


@administrator_required
def user_mods(request):
    users = yt_paginate(
        User.objects.filter(st__is_moderator=True, st__is_administrator=False).order_by('-date_joined', '-pk'),
        per_page=config.topics_per_page,
        page_number=request.GET.get('page', 1)
    )
    context = {'users': users, }
    return render(request, 'spirit/user/admin/mods.html', context)


@administrator_required
def user_unactive(request):
    users = yt_paginate(
        User.objects.filter(is_active=False).order_by('-date_joined', '-pk'),
        per_page=config.topics_per_page,
        page_number=request.GET.get('page', 1)
    )
    context = {'users': users, }
    return render(request, 'spirit/user/admin/unactive.html', context)
