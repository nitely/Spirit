from django import forms
from django.utils.translation import gettext_lazy as _

from .models import CommentLike


class LikeForm(forms.ModelForm):

    class Meta:
        model = CommentLike
        fields = []

    def __init__(self, user=None, comment=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.comment = comment

    def clean(self):
        cleaned_data = super().clean()

        like = CommentLike.objects.filter(user=self.user,
                                          comment=self.comment)

        if like.exists():
            # Do this since some of the unique_together fields are excluded.
            raise forms.ValidationError(_("This like already exists"))

        return cleaned_data

    def save(self, commit=True):
        if not self.instance.pk:
            self.instance.user = self.user
            self.instance.comment = self.comment

        return super().save(commit)
