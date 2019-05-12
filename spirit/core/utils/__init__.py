# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import json
import hashlib
import uuid
from contextlib import contextmanager

from django.core.files.storage import default_storage
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.utils import six


def render_form_errors(form):
    return render_to_string('spirit/utils/_form_errors.html', {'form': form, })


def json_response(data=None, status=200):
    # TODO: Use JsonResponse on Django 1.7
    data = data or {}
    return HttpResponse(json.dumps(data), content_type='application/json', status=status)


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise


def get_hash(bytes_iter):
    assert not isinstance(
        bytes_iter,
        (six.text_type, six.binary_type))  # Avoid gotcha

    # todo: test!
    md5 = hashlib.md5()

    for b in bytes_iter:
        md5.update(b)

    return md5.hexdigest()


def get_file_hash(file):
    return get_hash(file.chunks())


@contextmanager
def pushd(new_dir):
    """
    Usage:

    with pushd('./my_dir'):
        print(os.getcwd())  # ./my_dir

        with pushd('./my_dir/my_other_dir'):
            print(os.getcwd())  # ./my_dir/my_other_dir

        print(os.getcwd())  # ./my_dir
    """
    prev_dir = os.getcwd()
    os.chdir(new_dir)
    yield
    os.chdir(prev_dir)


def get_query_string(request, **params):
    """
    Adds params to current query string
    """
    # todo: test!
    query_dict = request.GET.copy()  # MultiValueDict

    for k, v in sorted(params.items()):
        query_dict[k] = v

    return query_dict.urlencode()


def hashed_filename(file):
    # Assume a valid extension
    _, ext = os.path.splitext(file.name)
    return '{name}{ext}'.format(
        name=get_file_hash(file),  # This is slow
        ext=ext.lower())


def safe_uuid():
    """Return url-safe uuid of 32 characters"""
    return uuid.uuid4().hex


def unique_filename(file):
    """
    Return the file's name as last component and \
    a unique ID as first component. \
    A unique ID is returned as filename if \
    the file's name is not valid. The extension \
    is assumed to be valid
    """
    name, ext = os.path.splitext(file.name)
    name = default_storage.get_valid_name(name)
    return os.path.join(
        safe_uuid(),
        '{name}{ext}'.format(
            name=name.lstrip('.') or safe_uuid(),
            ext=ext.lower()))


def generate_filename(file, hashed=False):
    if hashed:
        return hashed_filename(file)
    return unique_filename(file)
