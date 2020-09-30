# -*- coding: utf-8 -*-

import re

from django import forms
from django.db.models import Max
from django.utils.translation import gettext_lazy as _
from django.utils.encoding import smart_str
from django.utils import timezone

from ..models import Category


class CategoryForm(forms.ModelForm):

    class Meta:
        model = Category
        fields = (
            "parent",
            "title",
            "description",
            "is_global",
            "is_closed",
            "is_removed",
            "color")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = (
            Category.objects
            .visible()
            .parents()
            .ordered())

        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)

        self.fields['parent'] = forms.ModelChoiceField(
            queryset=queryset, required=False)
        self.fields['parent'].label_from_instance = (
            lambda obj: smart_str(obj.title))

    def clean_parent(self):
        parent = self.cleaned_data["parent"]

        if self.instance.pk:
            has_children = self.instance.category_set.all().exists()

            if parent and has_children:
                raise forms.ValidationError(
                    _("The category you are updating "
                      "can not have a parent since it has childrens"))

        return parent

    def clean_color(self):
        color = self.cleaned_data["color"]

        if color and not re.match(r'^#([A-Fa-f0-9]{3}){1,2}$', color):
            raise forms.ValidationError(
                _("The input is not a valid hex color."))

        return color

    def get_max_sort(self):
        return (
            Category.objects
            .aggregate(max_sort=Max('sort'))['max_sort'] or 0)

    def save(self, commit=True):
        if not self.instance.pk:
            self.instance.sort = self.get_max_sort() + 1
        self.instance.reindex_at = timezone.now()
        return super().save(commit)
