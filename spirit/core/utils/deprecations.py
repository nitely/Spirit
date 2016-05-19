# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import warnings

__all__ = [
    'RemovedInNextVersionWarning',
    'warn']


class RemovedInNextVersionWarning(DeprecationWarning):
    """"""


def warn(message):
    warnings.warn(
        message,
        RemovedInNextVersionWarning,
        stacklevel=2)


warnings.simplefilter("default", RemovedInNextVersionWarning)
