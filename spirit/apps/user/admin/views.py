# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.utils.translation import ugettext as _
from djconfig import config

from spirit.utils.paginator import yt_paginate
from spirit.utils.decorators import administrator_required
from .forms import UserForm, UserProfileForm


User = get_user_model()


@administrator_required
def edit(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        uform = UserForm(data=request.POST, instance=user)
        form = UserProfileForm(data=request.POST, instance=user.st)

        if all([uform.is_valid(), form.is_valid()]):
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
def _index(request, queryset, template):
    users = yt_paginate(
        queryset.order_by('-date_joined', '-pk'),
        per_page=config.topics_per_page,
        page_number=request.GET.get('page', 1)
    )
    context = {'users': users, }
    return render(request, template, context)


def index(request):
    return _index(
        request,
        queryset=User.objects.all(),
        template='spirit/user/admin/list.html'
    )


def admins(request):
    return _index(
        request,
        queryset=User.objects.filter(st__is_administrator=True),
        template='spirit/user/admin/admins.html'
    )


def mods(request):
    return _index(
        request,
        queryset=User.objects.filter(st__is_moderator=True, st__is_administrator=False),
        template='spirit/user/admin/mods.html'
    )


def unactive(request):
    return _index(
        request,
        queryset=User.objects.filter(is_active=False),
        template='spirit/user/admin/unactive.html'
    )
