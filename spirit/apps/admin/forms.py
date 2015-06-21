# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from djconfig.forms import ConfigForm
from django import forms
from django.utils.translation import ugettext_lazy as _


class BasicConfigForm(ConfigForm):

    site_name = forms.CharField(initial="Spirit", label=_("site name"))
    site_description = forms.CharField(initial="", label=_("site description"), max_length=75, required=False)
    template_footer = forms.CharField(initial="", label=_("footer snippet"), required=False,
                                      widget=forms.Textarea(attrs={'rows': 2, }),
                                      help_text=_("This gets rendered just before the footer in your template."))
    comments_per_page = forms.IntegerField(initial=20, label=_("comments per page"), min_value=1, max_value=100)
    topics_per_page = forms.IntegerField(initial=20, label=_("topics per page"), min_value=1, max_value=100)
