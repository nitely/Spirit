from django.core.files.storage import FileSystemStorage, default_storage, storages

from .conf import settings

__all__ = ["spirit_storage", "spirit_storage_or_none", "OverwriteFileSystemStorage"]


class OverwriteFileSystemStorage(FileSystemStorage):
    def get_available_name(self, name, **kwargs):
        self.delete(name)
        return name


def select_storage(default=default_storage):
    """returns ``None`` if there is no custom storage"""
    if not settings.ST_STORAGE:  # empty or None
        return default
    if settings.ST_STORAGE == "spirit.core.storage.OverwriteFileSystemStorage":
        return OverwriteFileSystemStorage()
    if settings.ST_STORAGE == "django.core.files.storage.FileSystemStorage":
        return FileSystemStorage()
    return storages[settings.ST_STORAGE]


spirit_storage_or_none = select_storage
spirit_storage = select_storage()
