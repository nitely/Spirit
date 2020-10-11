# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db import IntegrityError, transaction

from .managers import TopicNotificationQuerySet
from spirit.core.conf import settings


class TopicNotification(models.Model):
    UNDEFINED, MENTION, COMMENT = range(3)
    ACTION_CHOICES = (
        (UNDEFINED, _("Undefined")),
        (MENTION, _("Mention")),
        (COMMENT, _("Comment")))

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='st_topic_notifications',
        on_delete=models.CASCADE)
    topic = models.ForeignKey(
        'spirit_topic.Topic',
        on_delete=models.CASCADE)
    comment = models.ForeignKey(
        'spirit_comment.Comment',
        on_delete=models.CASCADE)

    date = models.DateTimeField(default=timezone.now)
    action = models.IntegerField(choices=ACTION_CHOICES, default=UNDEFINED)
    is_read = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    objects = TopicNotificationQuerySet.as_manager()

    class Meta:
        unique_together = ('user', 'topic')
        ordering = ['-date', '-pk']
        verbose_name = _("topic notification")
        verbose_name_plural = _("topics notification")

    def get_absolute_url(self):
        if self.topic_id != self.comment.topic_id:
            # Out of sync
            return self.topic.get_absolute_url()
        return self.comment.get_absolute_url()

    @property
    def text_action(self):
        return self.ACTION_CHOICES[self.action][1]

    @property
    def is_mention(self):
        return self.action == self.MENTION

    @property
    def is_comment(self):
        return self.action == self.COMMENT

    @classmethod
    def mark_as_read(cls, user, topic):
        if not user.is_authenticated:
            return

        (cls.objects
         .filter(user=user, topic=topic)
         .update(is_read=True))

    @classmethod
    def create_maybe(cls, user, comment, is_read=True, action=COMMENT):
        # Create a dummy notification
        return cls.objects.get_or_create(
            user=user,
            topic=comment.topic,
            defaults={
                'comment': comment,
                'action': action,
                'is_read': is_read,
                'is_active': True})

    @classmethod
    def notify_new_comment(cls, comment):
        (cls.objects
         .filter(topic=comment.topic, is_active=True, is_read=True)
         .exclude(user=comment.user)
         .update(
            comment=comment,
            is_read=False,
            action=cls.COMMENT,
            date=timezone.now()))

    @classmethod
    def notify_new_mentions(cls, comment, mentions):
        if not mentions:
            return

        # TODO: refactor
        for user in mentions.values():
            try:
                with transaction.atomic():
                    cls.objects.create(
                        user=user,
                        topic=comment.topic,
                        comment=comment,
                        action=cls.MENTION,
                        is_active=True)
            except IntegrityError:
                pass

        (cls.objects
         .filter(
            user__in=tuple(mentions.values()),
            topic=comment.topic,
            is_read=True)
         .update(
            comment=comment,
            is_read=False,
            action=cls.MENTION,
            date=timezone.now()))

    @classmethod
    def bulk_create(cls, users, comment):
        return cls.objects.bulk_create([
            cls(user=user,
                topic=comment.topic,
                comment=comment,
                action=cls.COMMENT,
                is_active=True)
            for user in users])

    # XXX add tests
    # XXX fix with migration (see issue #237)
    @classmethod
    def sync(cls, comment, topic):
        # Notifications can go out of sync
        # when the comment is no longer
        # within the topic (i.e moved).
        # User is subscribed to the topic,
        # not the comment, so we either update
        # it to a newer comment or set it as undefined
        if comment.topic_id == topic.pk:
            return
        next_comment = (
            topic.comment_set
                .filter(date__gt=comment.date)
                .order_by('date')
                .first())
        if next_comment is None:
            (cls.objects
             .filter(comment=comment, topic=topic)
             .update(is_read=True, action=cls.UNDEFINED))
            return
        (cls.objects
         .filter(comment=comment, topic=topic)
         .update(comment=next_comment, action=cls.COMMENT))
