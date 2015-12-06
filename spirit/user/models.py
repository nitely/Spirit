# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.db.models import F
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.contrib.auth.models import AbstractUser

from ..core.utils.timezone import TIMEZONE_CHOICES
from ..core.utils.models import AutoSlugField


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name=_("profile"), related_name='st')

    slug = AutoSlugField(populate_from="user.username", db_index=False, blank=True)
    location = models.CharField(_("location"), max_length=75, blank=True)
    last_seen = models.DateTimeField(_("last seen"), auto_now=True)
    last_ip = models.GenericIPAddressField(_("last ip"), blank=True, null=True)
    timezone = models.CharField(_("time zone"), max_length=32, choices=TIMEZONE_CHOICES, default='UTC')
    is_administrator = models.BooleanField(_('administrator status'), default=False)
    is_moderator = models.BooleanField(_('moderator status'), default=False)
    is_verified = models.BooleanField(_('verified'), default=False,
                                      help_text=_('Designates whether the user has verified his '
                                                  'account by email or by other means. Un-select this '
                                                  'to let the user activate his account.'))

    topic_count = models.PositiveIntegerField(_("topic count"), default=0)
    comment_count = models.PositiveIntegerField(_("comment count"), default=0)
    given_likes_count = models.PositiveIntegerField(_("given likes count"), default=0)
    received_likes_count = models.PositiveIntegerField(_("received likes count"), default=0)

    class Meta:
        verbose_name = _("forum profile")
        verbose_name_plural = _("forum profiles")

    def save(self, *args, **kwargs):
        if self.user.is_superuser:
            self.is_administrator = True

        if self.is_administrator:
            self.is_moderator = True

        super(UserProfile, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('spirit:user:detail', kwargs={'pk': self.user.pk, 'slug': self.slug})

    def increase_comment_count(self):
        UserProfile.objects.filter(pk=self.pk).update(comment_count=F('comment_count') + 1)

    def decrease_comment_count(self):
        UserProfile.objects.filter(pk=self.pk).update(comment_count=F('comment_count') - 1)

    def increase_topic_count(self):
        UserProfile.objects.filter(pk=self.pk).update(topic_count=F('topic_count') + 1)

    def decrease_topic_count(self):
        UserProfile.objects.filter(pk=self.pk).update(topic_count=F('topic_count') - 1)

    def increase_given_likes_count(self):
        UserProfile.objects.filter(pk=self.pk).update(given_likes_count=F('given_likes_count') + 1)

    def decrease_given_likes_count(self):
        UserProfile.objects.filter(pk=self.pk).update(given_likes_count=F('given_likes_count') - 1)

    def increase_received_likes_count(self):
        UserProfile.objects.filter(pk=self.pk).update(received_likes_count=F('received_likes_count') + 1)

    def decrease_received_likes_count(self):
        UserProfile.objects.filter(pk=self.pk).update(received_likes_count=F('received_likes_count') - 1)


class User(AbstractUser):
    # Backward compatibility

    class Meta(AbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL'
        ordering = ['-date_joined', '-pk']
        verbose_name = _('user')
        verbose_name_plural = _('users')
        db_table = 'spirit_user_user'
