# -*- coding: utf-8 -*-

from unittest import skipIf

import django
from django.test import TestCase, override_settings
from django.core.files.storage import Storage, FileSystemStorage, default_storage
from django.core.files.uploadedfile import SimpleUploadedFile

from . import utils as test_utils
from spirit.core.conf import settings
from spirit.core import storage

IS_DJANGO_LESSER_THAN_3_1 = django.VERSION[:2] < (3, 1)


class StorageTests(TestCase):

    def test_spirit_storage(self):
        self.assertIsInstance(storage.spirit_storage, Storage)

    @skipIf(not IS_DJANGO_LESSER_THAN_3_1, "Django >= 3.1")
    @skipIf(settings.ST_STORAGE is not None, "ST_STORAGE is not None")
    def test_spirit_storage_or_none(self):
        self.assertIsNone(storage.spirit_storage_or_none)

    @skipIf(not IS_DJANGO_LESSER_THAN_3_1, "Django >= 3.1")
    @skipIf(settings.ST_STORAGE is None, "ST_STORAGE is None")
    def test_spirit_storage_or_none_set(self):
        self.assertIs(
            type(storage.spirit_storage_or_none),
            type(storage.select_storage()))

    @skipIf(IS_DJANGO_LESSER_THAN_3_1, "Django < 3.1")
    def test_spirit_storage_or_none_callable(self):
        self.assertIs(
            storage.spirit_storage_or_none,
            storage.select_storage)

    def test_select_storage(self):
        with override_settings(ST_STORAGE=None):
            self.assertIsNone(storage.select_storage(default=None))
        with override_settings(ST_STORAGE=None):
            self.assertIs(storage.select_storage(), default_storage)
        with override_settings(ST_STORAGE='spirit.core.storage.OverwriteFileSystemStorage'):
            self.assertIsInstance(
                storage.select_storage(), storage.OverwriteFileSystemStorage)
        with override_settings(ST_STORAGE='django.core.files.storage.FileSystemStorage'):
            self.assertIsInstance(
                storage.select_storage(), FileSystemStorage)

    def test_overwrite_file_system(self):
        test_utils.clean_media()
        overwrite_storage = storage.OverwriteFileSystemStorage()
        self.assertIsInstance(overwrite_storage, FileSystemStorage)
        file = SimpleUploadedFile('foo.gif', content=b'foo')
        name = overwrite_storage.save('foo.gif', file)
        self.assertEqual(name, 'foo.gif')
        self.assertTrue(overwrite_storage.exists('foo.gif'))
        with overwrite_storage.open('foo.gif') as fh:
            self.assertEqual(fh.read(), b'foo')
        # overwrite
        file = SimpleUploadedFile('foo.gif', content=b'bar')
        name = overwrite_storage.save('foo.gif', file)
        self.assertEqual(name, 'foo.gif')
        self.assertTrue(overwrite_storage.exists('foo.gif'))
        with overwrite_storage.open('foo.gif') as fh:
            self.assertEqual(fh.read(), b'bar')
