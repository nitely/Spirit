# -*- coding: utf-8 -*-

from django.shortcuts import redirect
from django.utils.encoding import iri_to_uri

try:
    from django.utils.http import url_has_allowed_host_and_scheme
except ImportError:
    from django.utils.http import is_safe_url as url_has_allowed_host_and_scheme


def _resolve_lazy_url(url):
    if callable(url):
        return url()
    return url


def safe_redirect(request, key, default_url='', method='GET'):
    next = (
        getattr(request, method).get(key, None) or
        _resolve_lazy_url(default_url)
    )
    url_is_safe = url_has_allowed_host_and_scheme(
        url=next, allowed_hosts=None)
        #allowed_hosts=settings.ALLOWED_HOSTS,
        #require_https=request.is_secure())
    if url_is_safe:
        return redirect(iri_to_uri(next))
    return redirect('/')
