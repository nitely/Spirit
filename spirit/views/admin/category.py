#-*- coding: utf-8 -*-

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
    return render(request, 'spirit/admin/category/category_list.html', {'categories': categories, })


@administrator_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(data=request.POST)

        if form.is_valid():
            form.save()
            return redirect(reverse("spirit:admin-category-list"))
    else:
        form = CategoryForm()

    return render(request, 'spirit/admin/category/category_create.html', {'form': form, })


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

    return render(request, 'spirit/admin/category/category_update.html', {'form': form, })