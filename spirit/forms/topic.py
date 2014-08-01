#-*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _

from ..utils.forms import NestedModelChoiceField
from spirit.models.category import Category

from spirit.models.topic import Topic


class TopicForm(forms.ModelForm):

    class Meta:
        model = Topic
        fields = ('title', 'category')

    def __init__(self, user, *args, **kwargs):
        super(TopicForm, self).__init__(*args, **kwargs)
        self.user = user
        # TODO: add custom Prefetch object to filter closed sub-categories, on Django 1.7
        self.fields['category'] = NestedModelChoiceField(queryset=Category.objects.for_public_open(),
                                                         related_name='category_set',
                                                         parent_field='parent_id',
                                                         label_field='title',
                                                         label=_("Category"),
                                                         empty_label=_("Chose a category"))

        if self.instance.pk and not user.is_moderator:
            del self.fields['category']

    def clean_category(self):
        # TODO: remove this on django 1.7
        category = self.cleaned_data['category']

        if category.is_closed or category.is_removed:
            raise forms.ValidationError(_("The chosen category is closed"))

        return category

    def save(self, commit=True):
        if not self.instance.pk:
            self.instance.user = self.user

        return super(TopicForm, self).save(commit)