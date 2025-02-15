from datetime import datetime, timezone

from django.template import defaultfilters
from django.utils.timezone import is_aware
from django.utils.translation import gettext as _

from .registry import register


@register.filter(expects_localtime=True)
def shortnaturaltime(value):
    """
    now, 1s, 1m, 1h, 1 Ene, 1 Ene 2012
    """
    tz = timezone.utc if is_aware(value) else None
    now = datetime.now(tz)

    if value > now:  # Future
        return "{delta}".format(delta=defaultfilters.date(value, "j M 'y"))

    delta = now - value

    if delta.days:
        if defaultfilters.date(now, "y") == defaultfilters.date(value, "y"):
            return "{delta}".format(delta=defaultfilters.date(value, "j M"))

        return "{delta}".format(delta=defaultfilters.date(value, "j M 'y"))

    if not delta.seconds:
        return _("now")

    count = delta.seconds
    if count < 60:
        return _("%(count)ss") % {"count": count}

    count //= 60
    if count < 60:
        return _("%(count)sm") % {"count": count}

    count //= 60
    return _("%(count)sh") % {"count": count}
