# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy as _

from ..models import Category


class CategoryForm(forms.ModelForm):

    class Meta:
        model = Category
        fields = ("parent", "title", "description", "is_closed", "is_removed")

    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        queryset = Category.objects.visible().parents()

        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)

        self.fields['parent'] = forms.ModelChoiceField(queryset=queryset, required=False)

    def clean_parent(self):
        parent = self.cleaned_data["parent"]

        if self.instance.pk:
            has_childrens = self.instance.category_set.all().exists()

            if parent and has_childrens:
                raise forms.ValidationError(_("The category you are updating "
                                              "can not have a parent since it has childrens"))

        return parent