# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import hashlib

from django.utils.http import urlencode, urlquote

from .. import register


@register.simple_tag()
def get_gravatar_url(user, size, rating='g', default='identicon'):
    url = "http://www.gravatar.com/avatar/"
    hash = hashlib.md5(user.email.strip().lower().encode('utf-8')).hexdigest()
    data = urlencode([('d', urlquote(default)),
                      ('s', str(size)),
                      ('r', rating)])
    return "".join((url, hash, '?', data))
