# -*- coding: utf-8 -*-

from django.contrib.sites.shortcuts import get_current_site
from django.utils.translation import gettext as _
from django.template.loader import render_to_string

from spirit.core.conf import settings
from spirit.core import tasks
from .tokens import (
    UserActivationTokenGenerator,
    UserEmailChangeTokenGenerator)


def sender(request, subject, template_name, context, to):
    site = get_current_site(request)
    context.update({
        'site_name': site.name,
        'domain': site.domain,
        'protocol': 'https' if request.is_secure() else 'http'
    })
    message = render_to_string(template_name, context)

    # todo: remove in Spirit 0.5 (use DEFAULT_FROM_EMAIL)
    from_email = "{site_name} <{name}@{domain}>".format(
        name="noreply",
        domain=site.domain,
        site_name=site.name
    )

    # todo: remove
    if settings.DEFAULT_FROM_EMAIL != 'webmaster@localhost':
        from_email = settings.DEFAULT_FROM_EMAIL

    # Subject cannot contain new lines
    subject = ''.join(subject.splitlines())
    tasks.send_email(subject, message, from_email, to)


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
    context = {'token': token, }
    sender(request, subject, template_name, context, [user.email, ])
