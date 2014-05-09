#-*- coding: utf-8 -*-

from django import forms

from spirit.models.comment_bookmark import CommentBookmark


class BookmarkForm(forms.ModelForm):

    class Meta:
        model = CommentBookmark
        fields = ['comment_number', ]