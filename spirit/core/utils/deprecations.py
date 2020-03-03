# -*- coding: utf-8 -*-

import warnings

__all__ = [
    'RemovedInNextVersionWarning',
    'warn']


class RemovedInNextVersionWarning(DeprecationWarning):
    """"""


def warn(message, stacklevel=3):
    warnings.warn(
        message,
        category=RemovedInNextVersionWarning,
        stacklevel=stacklevel)


warnings.simplefilter("default", RemovedInNextVersionWarning)
