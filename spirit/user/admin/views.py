# -*- coding: utf-8 -*-

from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.utils.translation import gettext as _

from djconfig import config

from spirit.core.utils.http import safe_redirect
from spirit.core.utils.views import is_post, post_data
from spirit.core.utils.paginator import yt_paginate
from spirit.core.utils.decorators import administrator_required
from .forms import UserForm, UserProfileForm

User = get_user_model()


@administrator_required
def edit(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    uform = UserForm(data=post_data(request), instance=user)
    form = UserProfileForm(data=post_data(request), instance=user.st)
    if is_post(request) and all([uform.is_valid(), form.is_valid()]):
        uform.save()
        form.save()
        messages.info(request, _("This profile has been updated!"))
        return safe_redirect(request, "next", request.get_full_path())
    return render(
        request=request,
        template_name='spirit/user/admin/edit.html',
        context={'form': form, 'uform': uform})


@administrator_required
def _index(request, queryset, template):
    users = yt_paginate(
        queryset.order_by('-date_joined', '-pk'),
        per_page=config.topics_per_page,
        page_number=request.GET.get('page', 1)
    )
    return render(request, template, context={'users': users})


def index(request):
    return _index(
        request,
        queryset=User.objects.all(),
        template='spirit/user/admin/index.html'
    )


def index_admins(request):
    return _index(
        request,
        queryset=User.objects.filter(st__is_administrator=True),
        template='spirit/user/admin/admins.html'
    )


def index_mods(request):
    return _index(
        request,
        queryset=User.objects.filter(st__is_moderator=True, st__is_administrator=False),
        template='spirit/user/admin/mods.html'
    )


def index_unactive(request):
    return _index(
        request,
        queryset=User.objects.filter(is_active=False),
        template='spirit/user/admin/unactive.html'
    )
