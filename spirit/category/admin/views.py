# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib import messages
from django.utils.translation import ugettext as _

from ...core.conf import settings
from ...core.utils.decorators import administrator_required
from ..models import Category
from .forms import CategoryForm

User = get_user_model()


@administrator_required
def index(request):
    categories = Category.objects.filter(parent=None, is_private=False)
    context = {'categories': categories, }
    return render(request, 'spirit/category/admin/index.html', context)


@administrator_required
def create(request):
    if request.method == 'POST':
        form = CategoryForm(data=request.POST)

        if form.is_valid():
            form.save()
            return redirect(reverse("spirit:admin:category:index"))
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
            return redirect(reverse("spirit:admin:category:index"))
    else:
        form = CategoryForm(instance=category)

    context = {'form': form, }

    return render(request, 'spirit/category/admin/update.html', context)


@administrator_required
def move_up(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    sibling = Category.objects.filter(parent=category.parent, sort__lt=category.sort)\
        .exclude(pk=settings.ST_TOPIC_PRIVATE_CATEGORY_PK).order_by('-sort')[::1]
    if sibling:
        sort = category.sort
        category.sort = sibling[0].sort
        sibling[0].sort = sort
        category.save()
        sibling[0].save()
    return redirect(reverse("spirit:admin:category:index"))


@administrator_required
def move_dn(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    sibling = Category.objects.filter(parent=category.parent, sort__gt=category.sort)\
        .exclude(pk=settings.ST_TOPIC_PRIVATE_CATEGORY_PK).order_by('sort')[::1]
    if sibling:
        sort = category.sort
        category.sort = sibling[0].sort
        sibling[0].sort = sort
        category.save()
        sibling[0].save()
    return redirect(reverse("spirit:admin:category:index"))
