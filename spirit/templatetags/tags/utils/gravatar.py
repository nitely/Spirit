#-*- coding: utf-8 -*-


import hashlib

from django.utils.http import urlencode, urlquote
from django.utils.encoding import force_bytes

from .. import register


@register.simple_tag()
def get_gravatar_url(user, size, rating='g', default='identicon'):
    url = "http://www.gravatar.com/avatar/"
    hash = hashlib.md5(force_bytes(user.email.strip().lower().encode('utf_8'))).hexdigest()
    data = urlencode({'d': urlquote(default), 's': str(size), 'r': rating})
    return "".join((url, hash, '?', data))
