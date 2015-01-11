# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from djconfig.forms import ConfigForm

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model

from spirit.models.category import Category
from spirit.models.comment_flag import CommentFlag


User = get_user_model()


class UserEditForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ("username", "email", "location",
                  "timezone", "is_administrator", "is_moderator", "is_active")


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


class CommentFlagForm(forms.ModelForm):

    class Meta:
        model = CommentFlag
        fields = ("is_closed", )

    def __init__(self, user=None, *args, **kwargs):
        super(CommentFlagForm, self).__init__(*args, **kwargs)
        self.user = user

    def save(self, commit=True):
        self.instance.moderator = self.user
        return super(CommentFlagForm, self).save(commit)


class BasicConfigForm(ConfigForm):

    site_name = forms.CharField(initial="Spirit", label=_("site name"))
    site_description = forms.CharField(initial="", label=_("site description"), max_length=75, required=False)
    template_footer = forms.CharField(initial="", label=_("footer snippet"), required=False,
                                      widget=forms.Textarea(attrs={'rows': 2, }),
                                      help_text=_("This gets rendered just before the footer in your template."))
    comments_per_page = forms.IntegerField(initial=20, label=_("comments per page"), min_value=1, max_value=100)
    topics_per_page = forms.IntegerField(initial=20, label=_("topics per page"), min_value=1, max_value=100)
