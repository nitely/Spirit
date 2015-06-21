# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy as _

from spirit.utils.forms import NestedModelChoiceField
from ..category.models import Category
from .models import Topic


class TopicForm(forms.ModelForm):

    class Meta:
        model = Topic
        fields = ('title', 'category')

    def __init__(self, user, *args, **kwargs):
        super(TopicForm, self).__init__(*args, **kwargs)
        self.user = user
        self.fields['category'] = NestedModelChoiceField(queryset=Category.objects.visible().opened(),
                                                         related_name='category_set',
                                                         parent_field='parent_id',
                                                         label_field='title',
                                                         label=_("Category"),
                                                         empty_label=_("Chose a category"))

        if self.instance.pk and not user.st.is_moderator:
            del self.fields['category']

    def save(self, commit=True):
        if not self.instance.pk:
            self.instance.user = self.user

        return super(TopicForm, self).save(commit)
