# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.utils.translation import ugettext as _
from django.conf import settings
from django.utils import translation


def quotify(comment, username):
    """
    Converts 'Foo\nbar' to:
    > @username said:
    > Foo
    > bar
    \n\n
    """
    with translation.override(settings.LANGUAGE_CODE):
        header = _("@%(username)s said:") % {'username': username, }

    lines = comment.splitlines()
    quote = "\n> ".join(lines)
    quote = "> %(header)s\n> %(quote)s\n\n" % {'header': header, 'quote': quote}
    return quote
