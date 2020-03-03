# -*- coding: utf-8 -*-

from django import forms

from .models import CommentBookmark


class BookmarkForm(forms.ModelForm):

    class Meta:
        model = CommentBookmark
        fields = ['comment_number']

    def __init__(self, user=None, topic=None, *args, **kwargs):
        super(BookmarkForm, self).__init__(*args, **kwargs)
        self.user = user
        self.topic = topic

    def save(self, commit=True):
        # Bookmark is created/updated on topic view.
        CommentBookmark.increase_to(
            user=self.user,
            topic=self.topic,
            comment_number=self.cleaned_data['comment_number'])
