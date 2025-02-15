from django import forms
from django.utils.translation import gettext_lazy as _

from .models import TopicNotification


class NotificationForm(forms.ModelForm):

    is_active = forms.BooleanField(widget=forms.HiddenInput(), initial=True, required=False)

    class Meta:
        model = TopicNotification
        fields = ['is_active', ]


class NotificationCreationForm(NotificationForm):

    def __init__(self, user=None, topic=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.topic = topic

    def clean(self):
        cleaned_data = super().clean()

        notification = TopicNotification.objects.filter(
            user=self.user,
            topic=self.topic
        )

        if notification.exists():
            # Do this since some of the unique_together fields are excluded.
            raise forms.ValidationError(_("This notification already exists"))

        # todo: test!
        comment = self.topic.comment_set.last()

        if comment is None:
            raise forms.ValidationError(_("You can't subscribe to a topic with no comments"))

        return cleaned_data

    def save(self, commit=True):
        if not self.instance.pk:
            self.instance.user = self.user
            self.instance.topic = self.topic
            self.instance.comment = self.topic.comment_set.last()

        return super().save(commit)
