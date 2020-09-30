# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import gettext_lazy as _

from djconfig.forms import ConfigForm


class BasicConfigForm(ConfigForm):

    site_name = forms.CharField(initial="Spirit", label=_("site name"))
    site_description = forms.CharField(
        initial="", label=_("site description"), max_length=75, required=False)
    template_footer = forms.CharField(
        initial="", label=_("footer snippet"), required=False,
        widget=forms.Textarea(attrs={'rows': 2}),
        help_text=(
            "The footer snippet is no longer supported and "
            "it will be removed in future Spirit versions"))
    comments_per_page = forms.IntegerField(
        initial=20, label=_("comments per page"), min_value=1, max_value=100)
    topics_per_page = forms.IntegerField(
        initial=20, label=_("topics per page"), min_value=1, max_value=100)
