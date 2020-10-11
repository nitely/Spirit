# -*- coding: utf-8 -*-

import os
import logging

from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils.encoding import smart_bytes
from django.core.files.uploadedfile import TemporaryUploadedFile

from spirit.core.conf import settings
from spirit.core import utils
from spirit.core.storage import spirit_storage
from spirit.core.utils.markdown import Markdown
from spirit.topic.models import Topic
from .poll.models import CommentPoll, CommentPollChoice
from .models import Comment

logger = logging.getLogger(__name__)

# Mostly for Windows users who don't need file upload
try:
    import magic
except ImportError as err:
    # There used to be a logger.exception here but
    # the traceback made things confusing when an unhandled was raised
    if settings.ST_UPLOAD_FILE_ENABLED:
        logger.info(
            'File upload requires running: '
            '`pip install django-spirit[files]`')
        raise err
    magic = None


def save_user_file(user, file, subdir, hashed=False):
    """
    Save user media file into sub-dir. \
    The `hashed`` param prevents file duplication
    """
    file_path = utils.generate_filename(file, hashed=hashed)
    name = os.path.join('spirit', subdir, str(user.pk), file_path)
    name = spirit_storage.save(name, file)
    file.name = os.path.basename(name)
    file.url = spirit_storage.url(name)
    return file


class CommentForm(forms.ModelForm):
    comment = forms.CharField(
        label=_('Comment'),
        max_length=settings.ST_COMMENT_MAX_LEN,
        widget=forms.Textarea)
    comment_hash = forms.CharField(
        max_length=32,
        widget=forms.HiddenInput,
        required=False)

    class Meta:
        model = Comment
        fields = ['comment']

    def __init__(self, user=None, topic=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.topic = topic
        self.mentions = None  # {username: User, }
        self.polls = None  # {polls: [], choices: []}
        # Do not autofocus (when there's initial/instance),
        # we don't know where the cursor should be,
        # and that'd need JS anyway
        self.fields['comment'].widget.attrs['placeholder'] = _("Write comment...")

    def get_comment_hash(self):
        assert self.topic

        # This gets saved into
        # User.last_post_hash,
        # it does not matter whether
        # is a safe string or not
        comment_hash = self.cleaned_data.get('comment_hash', None)

        if comment_hash:
            return comment_hash

        return utils.get_hash((
            smart_bytes(self.cleaned_data['comment']),
            smart_bytes('thread-{}'.format(self.topic.pk))))

    def _get_comment_html(self):
        # user = self.user or self.instance.user
        markdown = Markdown()
        comment_html = markdown.render(self.cleaned_data['comment'])
        self.mentions = markdown.get_mentions()
        self.polls = markdown.get_polls()
        return comment_html

    def _save_polls(self):
        assert self.instance.pk
        assert self.polls is not None

        polls = self.polls['polls']
        choices = self.polls['choices']

        CommentPoll.update_or_create_many(comment=self.instance, polls_raw=polls)
        CommentPollChoice.update_or_create_many(comment=self.instance, choices_raw=choices)

    def save(self, commit=True):
        if not self.instance.pk:
            self.instance.user = self.user
            self.instance.topic = self.topic

        self.instance.comment_html = self._get_comment_html()
        comment = super(CommentForm, self).save(commit)

        if commit:
            self._save_polls()

        return comment


class CommentMoveForm(forms.Form):

    topic = forms.ModelChoiceField(queryset=Topic.objects.all(), widget=forms.TextInput)

    def __init__(self, topic, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['comments'] = forms.ModelMultipleChoiceField(
            queryset=Comment.objects.filter(topic=topic),
            widget=forms.CheckboxSelectMultiple)

    def save(self):
        comments = self.cleaned_data['comments']
        comments_list = list(comments)
        topic = self.cleaned_data['topic']
        comments.update(topic=topic)

        # Update topic in comment instance
        for c in comments_list:
            c.topic = topic

        return comments_list


class CommentImageForm(forms.Form):

    image = forms.ImageField(max_length=255)

    def __init__(self, user=None, *args, **kwargs):
        super(CommentImageForm, self).__init__(*args, **kwargs)
        self.user = user

    def clean_image(self):
        file = self.cleaned_data['image']
        ext = os.path.splitext(file.name)[1].lstrip('.').lower()

        if (ext not in settings.ST_ALLOWED_UPLOAD_IMAGE_FORMAT or
                file.image.format.lower() not in settings.ST_ALLOWED_UPLOAD_IMAGE_FORMAT):
            raise forms.ValidationError(
                _("Unsupported file format. Supported formats are %s.") %
                  ", ".join(settings.ST_ALLOWED_UPLOAD_IMAGE_FORMAT))

        return file

    def save(self):
        return save_user_file(
            user=self.user,
            file=self.cleaned_data['image'],
            subdir='images',
            hashed=settings.ST_PREVENT_SOME_FILE_DUPLICATION)


class CommentFileForm(forms.Form):

    file = forms.FileField(max_length=255)

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_file(self):
        file = self.cleaned_data['file']

        if not magic:
           raise forms.ValidationError(_("The file could not be validated"))

        # Won't ever raise. Has at most one '.' so lstrip is fine here
        ext = os.path.splitext(file.name)[1].lstrip('.').lower()
        if ext not in settings.ST_ALLOWED_UPLOAD_FILE_MEDIA_TYPE:
            raise forms.ValidationError(
                _("Unsupported file extension %(extension)s. "
                  "Supported extensions are %(supported)s.") % {
                    'extension': ext,
                    'supported': ", ".join(
                        sorted(settings.ST_ALLOWED_UPLOAD_FILE_MEDIA_TYPE.keys()))})

        try:
            if isinstance(file, TemporaryUploadedFile):
                file_mime = magic.from_file(file.temporary_file_path(), mime=True)
            else:  # In-memory file
                file_mime = magic.from_buffer(file.read(), mime=True)
        except magic.MagicException as e:
            logger.exception(e)
            raise forms.ValidationError(_("The file could not be validated"))

        mime = settings.ST_ALLOWED_UPLOAD_FILE_MEDIA_TYPE.get(ext, None)
        if mime != file_mime:
            raise forms.ValidationError(
                _("Unsupported file mime type %(mime)s. "
                  "Supported types are %(supported)s.") % {
                    'mime': file_mime,
                    'supported': ", ".join(
                        sorted(settings.ST_ALLOWED_UPLOAD_FILE_MEDIA_TYPE.values()))})

        return file

    def save(self):
        return save_user_file(
            user=self.user,
            file=self.cleaned_data['file'],
            subdir='files',
            hashed=settings.ST_PREVENT_SOME_FILE_DUPLICATION)
