# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.translation import ugettext as _

from spirit.utils.decorators import administrator_required
from spirit.models.category import Category

from spirit.forms.admin import CategoryForm


User = get_user_model()


@administrator_required
def category_list(request):
    categories = Category.objects.filter(parent=None, is_private=False)
    context = {'categories': categories, }
    return render(request, 'spirit/admin/category/category_list.html', context)


@administrator_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(data=request.POST)

        if form.is_valid():
            form.save()
            return redirect(reverse("spirit:admin-category-list"))
    else:
        form = CategoryForm()

    context = {'form': form, }

    return render(request, 'spirit/admin/category/category_create.html', context)


@administrator_required
def category_update(request, category_id):
    category = get_object_or_404(Category, pk=category_id)

    if request.method == 'POST':
        form = CategoryForm(data=request.POST, instance=category)

        if form.is_valid():
            form.save()
            messages.info(request, _("The category has been updated!"))
            return redirect(reverse("spirit:admin-category-list"))
    else:
        form = CategoryForm(instance=category)

    context = {'form': form, }

    return render(request, 'spirit/admin/category/category_update.html', context)
