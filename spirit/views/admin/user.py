# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.utils.translation import ugettext as _

from spirit.utils.decorators import administrator_required

from spirit.forms.admin import UserEditForm


User = get_user_model()


@administrator_required
def user_edit(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        form = UserEditForm(data=request.POST, instance=user)

        if form.is_valid():
            form.save()
            messages.info(request, _("This profile has been updated!"))
            return redirect(request.GET.get("next", request.get_full_path()))
    else:
        form = UserEditForm(instance=user)

    context = {'form': form, }

    return render(request, 'spirit/admin/user/user_edit.html', context)


@administrator_required
def user_list(request):
    # TODO: paginate
    users = User.objects.all()
    context = {'users': users, }
    return render(request, 'spirit/admin/user/user_list.html', context)


@administrator_required
def user_admins(request):
    users = User.objects.filter(is_administrator=True)
    context = {'users': users, }
    return render(request, 'spirit/admin/user/user_admins.html', context)


@administrator_required
def user_mods(request):
    users = User.objects.filter(is_moderator=True, is_administrator=False)
    context = {'users': users, }
    return render(request, 'spirit/admin/user/user_mods.html', context)


@administrator_required
def user_unactive(request):
    users = User.objects.filter(is_active=False)
    context = {'users': users, }
    return render(request, 'spirit/admin/user/user_unactive.html', context)
