# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy as _

from spirit.models.topic_favorite import TopicFavorite


class FavoriteForm(forms.ModelForm):

    class Meta:
        model = TopicFavorite
        fields = []

    def __init__(self, user=None, topic=None, *args, **kwargs):
        super(FavoriteForm, self).__init__(*args, **kwargs)
        self.user = user
        self.topic = topic

    def clean(self):
        cleaned_data = super(FavoriteForm, self).clean()

        favorite = TopicFavorite.objects.filter(user=self.user,
                                                topic=self.topic)

        if favorite.exists():
            # Do this since some of the unique_together fields are excluded.
            raise forms.ValidationError(_("This favorite already exists"))

        return cleaned_data

    def save(self, commit=True):
        if not self.instance.pk:
            self.instance.user = self.user
            self.instance.topic = self.topic

        return super(FavoriteForm, self).save(commit)
