# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.translation import ugettext as _

from spirit.utils.decorators import administrator_required
from ..models import Category
from .forms import CategoryForm


User = get_user_model()


@administrator_required
def index(request):
    categories = Category.objects.filter(parent=None, is_private=False)
    context = {'categories': categories, }
    return render(request, 'spirit/category/admin/list.html', context)


@administrator_required
def create(request):
    if request.method == 'POST':
        form = CategoryForm(data=request.POST)

        if form.is_valid():
            form.save()
            return redirect(reverse("spirit:admin-category-list"))
    else:
        form = CategoryForm()

    context = {'form': form, }

    return render(request, 'spirit/category/admin/create.html', context)


@administrator_required
def update(request, category_id):
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

    return render(request, 'spirit/category/admin/update.html', context)
