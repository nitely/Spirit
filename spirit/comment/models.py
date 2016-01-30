# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.db.models.signals import post_save, post_delete
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.conf import settings
from django.db.models import F
from django.utils import timezone

from trusts.models import Content

from .managers import CommentQuerySet

COMMENT_MAX_LEN = 3000  # changing this needs migration

COMMENT, MOVED, CLOSED, UNCLOSED, PINNED, UNPINNED = range(6)

ACTION = (
    (COMMENT, _("comment")),
    (MOVED, _("topic moved")),
    (CLOSED, _("topic closed")),
    (UNCLOSED, _("topic unclosed")),
    (PINNED, _("topic pinned")),
    (UNPINNED, _("topic unpinned")),
)


class Comment(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='st_comments')
    topic = models.ForeignKey('spirit_topic.Topic')

    comment = models.TextField(_("comment"), max_length=COMMENT_MAX_LEN)
    comment_html = models.TextField(_("comment html"))
    action = models.IntegerField(_("action"), choices=ACTION, default=COMMENT)
    date = models.DateTimeField(default=timezone.now)
    is_removed = models.BooleanField(default=False)
    is_modified = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    modified_count = models.PositiveIntegerField(_("modified count"), default=0)
    likes_count = models.PositiveIntegerField(_("likes count"), default=0)

    objects = CommentQuerySet.as_manager()

    class Meta:
        ordering = ['-date', '-pk']
        verbose_name = _("comment")
        verbose_name_plural = _("comments")

    def get_absolute_url(self):
        return reverse('spirit:comment:find', kwargs={'pk': str(self.id), })

    @property
    def like(self):
        # *likes* is dynamically created by manager.with_likes()
        try:
            assert len(self.likes) <= 1, "Panic, too many likes"
            return self.likes[0]
        except (AttributeError, IndexError):
            return

    def increase_modified_count(self):
        Comment.objects\
            .filter(pk=self.pk)\
            .update(modified_count=F('modified_count') + 1)

    def increase_likes_count(self, acting_user):
        Comment.objects\
            .filter(pk=self.pk)\
            .update(likes_count=F('likes_count') + 1)
        if not self.topic.category.is_private:
            self.user.st.increase_received_likes_count()
            acting_user.st.increase_given_likes_count()

    def decrease_likes_count(self, acting_user):
        Comment.objects\
            .filter(pk=self.pk)\
            .update(likes_count=F('likes_count') - 1)
        if not self.topic.category.is_private:
            self.user.st.decrease_received_likes_count()
            acting_user.st.decrease_given_likes_count()

    @classmethod
    def create_moderation_action(cls, user, topic, action):
        # TODO: better comment_html text (map to actions), use default language
        return cls.objects.create(
            user=user,
            topic=topic,
            action=action,
            comment="action",
            comment_html="action"
        )
Content.register_content(Comment, '%s__comment' % Content.get_content_fieldlookup('spirit_topic.Topic'))
Content.register_permission_condition(Comment, 'own', lambda u, p, o: u == o.user)

def increase_user_profile_comment_count(sender, instance, created, **kwargs):
    if created and not instance.topic.category.is_private:
        instance.user.st.increase_comment_count()

post_save.connect(increase_user_profile_comment_count, sender=Comment, dispatch_uid='Comment:increase_user_profile_comment_count')


def decrease_user_profile_comment_count(sender, instance, **kwargs):
    if not instance.topic.category.is_private:
        instance.user.st.decrease_comment_count()

post_delete.connect(decrease_user_profile_comment_count, sender=Comment, dispatch_uid='Comment:decrease_user_profile_comment_count')
