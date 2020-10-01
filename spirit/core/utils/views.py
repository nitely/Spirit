# -*- coding: utf-8 -*-


def is_post(request):
    """Check request is a POST"""
    return request.method == 'POST'


def post_data(request):
    """Return POST data or ``None`` if not a POST"""
    if is_post(request):
        return request.POST
    return None


def post_files(request):
    if is_post(request):
        return request.FILES
    return None


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'
