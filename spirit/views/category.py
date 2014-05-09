#-*- coding: utf-8 -*-

from django.views.generic import ListView
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponsePermanentRedirect

from spirit.models.topic import Topic

from spirit.models.category import Category


def category_detail(request, pk, slug):
    category = Category.objects.get_public_or_404(pk=pk)

    if category.slug != slug:
        return HttpResponsePermanentRedirect(category.get_absolute_url())

    subcategories = Category.objects.for_parent(parent=category)
    topics = Topic.objects.for_category(category=category)\
        .order_by('-is_pinned', '-last_active')\
        .select_related('category')

    return render(request, 'spirit/category/category_detail.html', {'category': category,
                                                                    'subcategories': subcategories,
                                                                    'topics': topics})


class CategoryList(ListView):

    template_name = 'spirit/category/category_list.html'
    context_object_name = "categories"
    queryset = Category.objects.for_parent()