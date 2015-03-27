# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import re

from django.db import models
from django.core.urlresolvers import reverse
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.core.mail import send_mail
from django.core import validators
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from spirit.utils.timezone import TIMEZONE_CHOICES
from spirit.utils.models import AutoSlugField


class AbstractForumUser(models.Model):
    slug = AutoSlugField(populate_from="username", db_index=False, blank=True)
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

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.is_administrator = True

        if self.is_administrator:
            self.is_moderator = True

        super(AbstractForumUser, self).save(*args, **kwargs)


class AbstractUser(AbstractBaseUser, PermissionsMixin, AbstractForumUser):
    # almost verbatim copy from the auth user model
    # adds username(db_index=True), email(unique=True, blank=False, max_length=254)
    username = models.CharField(_("username"), max_length=30, unique=True, db_index=True,
                                help_text=_('Required. 30 characters or fewer. Letters, numbers and '
                                            '@/./+/-/_ characters'),
                                validators=[
                                    validators.RegexValidator(re.compile('^[\w.@+-]+$'), _('Enter a valid username.'),
                                                              'invalid')
        ])
    first_name = models.CharField(_("first name"), max_length=30, blank=True)
    last_name = models.CharField(_("last name"), max_length=30, blank=True)
    email = models.EmailField(_("email"), max_length=254, unique=True)
    is_staff = models.BooleanField(_('staff status'), default=False,
                                   help_text=_('Designates whether the user can log into this admin '
                                               'site.'))
    is_active = models.BooleanField(_('active'), default=True,
                                    help_text=_('Designates whether this user should be treated as '
                                                'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', ]

    class Meta:
        abstract = True

    def get_absolute_url(self):
        return reverse('spirit:profile-detail', kwargs={'pk': self.pk,
                                                        'slug': self.slug})

    def get_full_name(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def email_user(self, subject, message, from_email=None):
        send_mail(subject, message, from_email, [self.email, ])


class User(AbstractUser):

    class Meta(AbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL'
        app_label = 'spirit'
        ordering = ['-date_joined', '-pk']
        verbose_name = _('user')
        verbose_name_plural = _('users')
