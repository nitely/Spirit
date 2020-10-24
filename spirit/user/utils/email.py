# -*- coding: utf-8 -*-

from django.utils.translation import gettext as _
from django.template.loader import render_to_string

from djconfig import config

from spirit.core.utils import site_url
from spirit.core import tasks
from .tokens import (
    UserActivationTokenGenerator,
    UserEmailChangeTokenGenerator)


# XXX remove; use tasks for everything
def sender(request, subject, template_name, context, to):
    context['site'] = site_url()
    context['site_name'] = config.site_name
    message = render_to_string(template_name, context)
    # Subject cannot contain new lines
    subject = ''.join(subject.splitlines())
    tasks.send_email(subject, message, to)


def send_activation_email(request, user):
    subject = _("User activation")
    template_name = 'spirit/user/activation_email.html'
    token = UserActivationTokenGenerator().generate(user)
    context = {'user_id': user.pk, 'token': token}
    sender(request, subject, template_name, context, [user.email, ])


def send_email_change_email(request, user, new_email):
    subject = _("Email change")
    template_name = 'spirit/user/email_change_email.html'
    token = UserEmailChangeTokenGenerator().generate(user, new_email)
    context = {'token': token}
    sender(request, subject, template_name, context, [user.email, ])
