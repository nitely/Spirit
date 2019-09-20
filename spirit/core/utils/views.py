# -*- coding: utf-8 -*-


def is_post(request):
    """Check request is a POST"""
    return request.method == 'POST'


def post_data(request):
    """Return POST data or ``None`` if not a POST"""
    if is_post(request):
        return request.POST
    return None
