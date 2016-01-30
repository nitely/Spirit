# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings


def load_backend(path):
    return import_string(path)()

def _get_backends(return_tuples=False):
    backends = []
    for backend_path in settings.SPIRIT_PERMISSION_BACKENDS:
        backend = load_backend(backend_path)
        backends.append((backend, backend_path) if return_tuples else backend)
    if not backends:
        raise ImproperlyConfigured(
            'No authentication backends have been defined. Does '
            'SPIRIT_PERMISSION_BACKENDS contain anything?'
        )
    return backends

def get_backends():
    return _get_backends(return_tuples=False)

default_app_config = 'spirit.user.perm.apps.SpiritPermAuthConfig'
