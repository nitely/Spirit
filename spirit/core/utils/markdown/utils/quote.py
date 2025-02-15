import re

from django.utils import translation
from django.utils.translation import gettext as _

from ....conf import settings

_PATTERN_POLL = re.compile(
    r"^(?:\[poll[^\]]*\])\n+"
    r"(?:[0-9]+[^\n]*\n+)+"
    r"(?:\[/poll\])",
    flags=re.MULTILINE,
)


def _strip_polls(comment):
    return re.sub(_PATTERN_POLL, r"", comment)


def quotify(comment, username):
    """
    Converts 'Foo\nbar' to:
    > @username said:
    > Foo
    > bar
    \n\n
    """
    with translation.override(settings.LANGUAGE_CODE):
        header = _("@%(username)s said:") % {"username": username}

    comment = _strip_polls(comment)
    lines = comment.splitlines()
    quote = "\n> ".join(lines)
    quote = f"> {header}\n> {quote}\n\n"
    return quote
