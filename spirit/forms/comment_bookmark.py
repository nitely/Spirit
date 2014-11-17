# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import forms

from spirit.models.comment_bookmark import CommentBookmark


class BookmarkForm(forms.ModelForm):

    class Meta:
        model = CommentBookmark
        fields = ['comment_number', ]

    def __init__(self, user=None, topic=None, *args, **kwargs):
        super(BookmarkForm, self).__init__(*args, **kwargs)
        self.user = user
        self.topic = topic

    def save(self, commit=True):
        comment_number = self.cleaned_data['comment_number']

        # Bookmark is created/updated on topic view.
        CommentBookmark.objects.filter(user=self.user, topic=self.topic)\
            .update(comment_number=comment_number)
