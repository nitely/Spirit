# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils import timezone
from django.db.models import F

from .managers import TopicQuerySet
from ..core.utils.models import AutoSlugField
from ..core.conf import settings


class Topic(models.Model):
    """
    Topic model

    :ivar last_active: Last time a comment was added/removed,\
    it makes the search re-index the topic
    :vartype last_active: `:py:class:models.DateTimeField`
    :ivar reindex_at: Last time this model was marked\
    for reindex. It makes the search re-index the topic,\
    it must be set explicitly
    :vartype reindex_at: `:py:class:models.DateTimeField`
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='st_topics',
        on_delete=models.CASCADE)
    category = models.ForeignKey(
        'spirit_category.Category',
        verbose_name=_("category"),
        on_delete=models.CASCADE)

    title = models.CharField(_("title"), max_length=255)
    slug = AutoSlugField(populate_from="title", db_index=False, blank=True)
    date = models.DateTimeField(_("date"), default=timezone.now)
    last_active = models.DateTimeField(_("last active"), default=timezone.now)
    reindex_at = models.DateTimeField(_("reindex at"), default=timezone.now)

    is_pinned = models.BooleanField(_("pinned"), default=False)
    is_globally_pinned = models.BooleanField(_("globally pinned"), default=False)
    is_closed = models.BooleanField(_("closed"), default=False)
    is_removed = models.BooleanField(default=False)

    view_count = models.PositiveIntegerField(_("views count"), default=0)
    comment_count = models.PositiveIntegerField(_("comment count"), default=0)

    objects = TopicQuerySet.as_manager()

    class Meta:
        ordering = ['-last_active', '-pk']
        verbose_name = _("topic")
        verbose_name_plural = _("topics")

    def get_absolute_url(self):
        if self.category_id == settings.ST_TOPIC_PRIVATE_CATEGORY_PK:
            return reverse(
                'spirit:topic:private:detail',
                kwargs={'topic_id': str(self.id), 'slug': self.slug})
        return reverse(
            'spirit:topic:detail',
            kwargs={'pk': str(self.id), 'slug': self.slug})

    def get_bookmark_url(self):
        if not self.is_visited:
            return self.get_absolute_url()

        if not self.has_new_comments:
            return self.bookmark.get_absolute_url()

        return self.bookmark.get_new_comment_url()

    @property
    def main_category(self):
        return self.category.parent or self.category

    @property
    def bookmark(self):
        # *bookmarks* is dynamically created by manager.with_bookmarks()
        try:
            assert len(self.bookmarks) <= 1, "Panic, too many bookmarks"
            return self.bookmarks[0]
        except (AttributeError, IndexError):
            return

    @property
    def new_comments_count(self):
        # This may not be accurate since bookmarks requires JS,
        # without JS only the first comment in a page is marked,
        # so this counter should be shown running a JS script
        if not self.bookmark:
            return 0

        # Comments may have been moved
        return max(0, self.comment_count - self.bookmarks[0].comment_number)

    @property
    def has_new_comments(self):
        return self.new_comments_count > 0

    @property
    def is_visited(self):
        return bool(self.bookmark)

    def increase_view_count(self):
        (Topic.objects
         .filter(pk=self.pk)
         .update(view_count=F('view_count') + 1))

    def increase_comment_count(self):
        (Topic.objects
         .filter(pk=self.pk)
         .update(comment_count=F('comment_count') + 1, last_active=timezone.now()))

    def decrease_comment_count(self):
        # todo: update last_active to last() comment
        (Topic.objects
         .filter(pk=self.pk)
         .update(comment_count=F('comment_count') - 1))

    def get_all_comments_html(self):
        """
        For search indexing

        :return: List of comments in HTML
        """
        return self.comment_set.values_list('comment_html', flat=True)
