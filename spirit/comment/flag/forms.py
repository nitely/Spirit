# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.db import IntegrityError
from django.utils import timezone

from .models import Flag, CommentFlag


class FlagForm(forms.ModelForm):

    class Meta:
        model = Flag
        fields = ['reason', 'body']

    def __init__(self, user=None, comment=None, *args, **kwargs):
        super(FlagForm, self).__init__(*args, **kwargs)
        self.user = user
        self.comment = comment

    def clean(self):
        cleaned_data = super(FlagForm, self).clean()

        flag = Flag.objects.filter(user=self.user,
                                   comment=self.comment)

        if flag.exists():
            # Do this since some of the unique_together fields are excluded.
            raise forms.ValidationError(_("This flag already exists"))

        return cleaned_data

    def save(self, commit=True):
        if not self.instance.pk:
            self.instance.user = self.user
            self.instance.comment = self.comment

            try:
                CommentFlag.objects.update_or_create(comment=self.comment,
                                                     defaults={'date': timezone.now(), })
            except IntegrityError:
                pass

        return super(FlagForm, self).save(commit)
