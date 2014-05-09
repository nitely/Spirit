#-*- coding: utf-8 -*-

import urllib
import hashlib

from .. import register


@register.simple_tag()
def get_gravatar_url(user, size, rating='g', default='identicon'):
    url = "http://www.gravatar.com/avatar/"
    hash = hashlib.md5(user.email.strip().lower()).hexdigest()
    data = urllib.urlencode({'d': urllib.quote(default), 's': str(size), 'r': rating})
    return "".join((url, hash, '?', data))
