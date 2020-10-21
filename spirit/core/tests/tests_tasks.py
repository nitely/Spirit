# -*- coding: utf-8 -*-

import datetime
from unittest import skipIf

from django.test import TestCase, override_settings
from django.core import mail
from django.core.management import call_command
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile

from haystack.query import SearchQuerySet

from . import utils as test_utils
from spirit.core import tasks
from spirit.core.tests.models import TaskResultModel
from spirit.core.storage import spirit_storage

try:
    @tasks.task_manager('celery')
    def celery_task(s):
        TaskResultModel.objects.create(result=s)
except ImportError:
    celery_task = None

try:
    @tasks.task_manager('huey')
    def huey_task(s):
        TaskResultModel.objects.create(result=s)
except ImportError:
    huey_task = None

@tasks.task_manager(None)
def none_task(s):
    TaskResultModel.objects.create(result=s)

try:
    _periodic_task = tasks.periodic_task_manager('celery')
    @_periodic_task(hours=10)
    def celery_periodic_task(s):
        TaskResultModel.objects.create(result=s)
except ImportError:
    celery_periodic_task = None

try:
    _periodic_task = tasks.periodic_task_manager('huey')
    @_periodic_task(hours=10)
    def huey_periodic_task(s):
        TaskResultModel.objects.create(result=s)
except ImportError:
    huey_periodic_task = None

_periodic_task = tasks.periodic_task_manager(None)
@_periodic_task(hours=10)
def none_periodic_task(s):
    TaskResultModel.objects.create(result=s)


def rebuild_index():
    call_command("rebuild_index", verbosity=0, interactive=False)


class TasksTests(TestCase):

    @test_utils.immediate_on_commit
    def test_task_manager_none(self):
        none_task('none')
        self.assertEqual(
            TaskResultModel.objects.last().result, 'none')

    @skipIf(celery_task is None, "Celery is not installed")
    @test_utils.immediate_on_commit
    def test_task_manager_celery(self):
        celery_task('celery')
        self.assertEqual(
            TaskResultModel.objects.last().result, 'celery')

    @skipIf(huey_task is None, "Huey is not installed")
    @test_utils.immediate_on_commit
    def test_task_manager_huey(self):
        huey_task('huey')
        self.assertEqual(
            TaskResultModel.objects.last().result, 'huey')

    @override_settings(DEFAULT_FROM_EMAIL="foobar_from@foo.com")
    @test_utils.immediate_on_commit
    def test_send_email(self):
        tasks.send_email(
            subject="foobar_sub",
            message="foobar_msg",
            recipients=['foo@foo.com', 'bar@bar.com'])
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].subject, "foobar_sub")
        self.assertEqual(mail.outbox[1].subject, "foobar_sub")
        self.assertEqual(mail.outbox[0].from_email, "foobar_from@foo.com")
        self.assertEqual(mail.outbox[1].from_email, "foobar_from@foo.com")
        self.assertEqual(mail.outbox[0].body, "foobar_msg")
        self.assertEqual(mail.outbox[1].body, "foobar_msg")
        self.assertEqual(mail.outbox[0].to, ['foo@foo.com'])
        self.assertEqual(mail.outbox[1].to, ['bar@bar.com'])

    @override_settings(ST_TASK_MANAGER='test')
    @test_utils.immediate_on_commit
    def test_search_index_update(self):
        rebuild_index()
        topic = test_utils.create_topic(test_utils.create_category())
        tasks.search_index_update(topic.pk)
        sq = SearchQuerySet().models(topic.__class__)
        self.assertEqual([s.object for s in sq], [topic])

    @override_settings(ST_TASK_MANAGER=None)
    @test_utils.immediate_on_commit
    def test_search_index_update_no_task_manager(self):
        rebuild_index()
        topic = test_utils.create_topic(test_utils.create_category())
        tasks.search_index_update(topic.pk)
        sq = SearchQuerySet().models(topic.__class__)
        self.assertEqual([s.object for s in sq], [])

    @test_utils.immediate_on_commit
    def test_none_periodic_task(self):
        none_periodic_task('none')
        self.assertEqual(
            TaskResultModel.objects.last().result, 'none')

    @skipIf(celery_periodic_task is None, "Celery is not installed")
    @test_utils.immediate_on_commit
    def test_celery_periodic_task(self):
        celery_periodic_task('celery')
        self.assertEqual(
            TaskResultModel.objects.last().result, 'celery')

    @skipIf(huey_periodic_task is None, "Huey is not installed")
    @test_utils.immediate_on_commit
    def test_huey_periodic_task(self):
        huey_periodic_task('huey')
        self.assertEqual(
            TaskResultModel.objects.last().result, 'huey')

    @test_utils.immediate_on_commit
    def test_full_search_index_update(self):
        rebuild_index()
        at_date = timezone.now() - datetime.timedelta(days=99)
        test_utils.create_topic(
            category=test_utils.create_category(reindex_at=at_date),
            last_active=at_date,
            reindex_at=at_date)
        topic = test_utils.create_topic(test_utils.create_category())
        tasks.full_search_index_update()
        sq = SearchQuerySet().models(topic.__class__)
        self.assertEqual([s.object for s in sq], [topic])

    @test_utils.with_test_storage
    @test_utils.immediate_on_commit
    @override_settings(ST_ALLOWED_AVATAR_FORMAT=('gif',))
    def test_make_avatars(self):
        test_utils.clean_media()
        content = (
            b'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00'
            b'\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')
        file = SimpleUploadedFile(
            'foo.gif', content=content, content_type='image/gif')
        user = test_utils.create_user()
        user.st.avatar = file
        user.st.save()
        self.assertTrue(spirit_storage.exists(user.st.avatar.name))
        tasks.make_avatars(user.pk)
        # original image is deleted
        self.assertFalse(spirit_storage.exists(user.st.avatar.name))
        user.refresh_from_db()
        self.assertTrue(spirit_storage.exists(user.st.avatar.name))
        self.assertEqual(
            user.st.avatar.name,
            'spirit/avatars/{}/pic_test.jpg'.format(user.pk))
        self.assertTrue(spirit_storage.exists(
            'spirit/avatars/{}/pic_test_small_test.jpg'.format(user.pk)))

    @test_utils.immediate_on_commit
    @override_settings(
        ST_TASK_MANAGER='tests', ST_SITE_URL='https://tests.com/')
    def test_notify_reply(self):
        user1 = test_utils.create_user()
        user2 = test_utils.create_user()
        user3 = test_utils.create_user()
        comment = test_utils.create_comment()
        test_utils.create_notification(
            comment, user1, is_read=False, action='reply')
        test_utils.create_notification(
            comment, user2, is_read=False, action='reply')
        test_utils.create_notification(
            comment, user3, is_read=True, action='reply')
        test_utils.create_notification(is_read=True, action='reply')
        test_utils.create_notification(is_read=False, action='reply')
        tasks.notify_reply(comment_id=comment.pk)
        self.assertEqual(len(mail.outbox), 2)
