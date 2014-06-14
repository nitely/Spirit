#-*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.db import IntegrityError
from django.utils import timezone

from spirit.models.comment_flag import Flag, CommentFlag


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

            # TODO: use update_or_create on django 1.7
            try:
                CommentFlag.objects.create(comment=self.comment)
            except IntegrityError:
                CommentFlag.objects.filter(comment=self.comment)\
                    .update(date=timezone.now())

        return super(FlagForm, self).save(commit)