# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from datetime import datetime

from django.template import defaultfilters
from django.utils.translation import ugettext as _
from django.utils.timezone import is_aware, utc

from .. import register


@register.filter(expects_localtime=True)
def shortnaturaltime(value):
    """
    now, 1s, 1m, 1h, 1 Ene, 1 Ene 2012
    """
    tz = utc if is_aware(value) else None
    now = datetime.now(tz)

    if value > now:  # Future
        return '%(delta)s' % {'delta': defaultfilters.date(value, 'j M \'y')}

    delta = now - value

    if delta.days:
        if defaultfilters.date(now, 'y') == defaultfilters.date(value, 'y'):
            return '%(delta)s' % {'delta': defaultfilters.date(value, 'j M')}

        return '%(delta)s' % {'delta': defaultfilters.date(value, 'j M \'y')}

    if not delta.seconds:
        return _('now')

    count = delta.seconds
    if count < 60:
        return _('%(count)ss') % {'count': count}

    count //= 60
    if count < 60:
        return _('%(count)sm') % {'count': count}

    count //= 60
    return _('%(count)sh') % {'count': count}
