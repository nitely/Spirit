# -*- coding: utf-8 -*-

import django
from django.core.files.storage import (
    FileSystemStorage, default_storage, get_storage_class)

from .conf import settings

__all__ = [
    'spirit_storage',
    'spirit_storage_or_none',
    'OverwriteFileSystemStorage']


def select_storage():
    """returns ``None`` if there is no custom storage"""
    if settings.ST_STORAGE is None:
        return None
    if settings.ST_STORAGE == 'spirit.core.storage.OverwriteFileSystemStorage':
        return OverwriteFileSystemStorage()
    return get_storage_class(settings.ST_STORAGE)()


# In Django +3.1 the callback can be passed to FileField
# storage, and it won't create a migration
if django.VERSION[:2] >= (3, 1):
    spirit_storage_or_none = select_storage
else:
    spirit_storage_or_none = select_storage()

spirit_storage = select_storage() or default_storage


class OverwriteFileSystemStorage(FileSystemStorage):
    def get_available_name(self, name, **kwargs):
        self.delete(name)
        return name
