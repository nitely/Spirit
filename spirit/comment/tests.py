# -*- coding: utf-8 -*-

import os
import json
import shutil
import hashlib
import io
from unittest import skipIf

from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.template import Template, Context
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.utils import override_settings
from django.core import mail

from . import forms as comment_forms
from spirit.core.conf import settings
from spirit.core.tests import utils
from .models import Comment
from .forms import (
    CommentForm,
    CommentMoveForm,
    CommentImageForm,
    CommentFileForm)
from .tags import render_comments_form
from spirit.core.utils import markdown
from .views import delete as comment_delete
from spirit.topic.models import Topic
from spirit.category.models import Category
from spirit.user.models import UserProfile
from .history.models import CommentHistory
from .utils import comment_posted, pre_comment_update, post_comment_update
from spirit.topic.notification.models import TopicNotification
from spirit.topic.unread.models import TopicUnread
from .poll.models import CommentPoll
from . import views

MENTION = TopicNotification.MENTION
User = get_user_model()


class CommentViewTest(TestCase):

    def setUp(self):
        utils.cache_clear()
        self.user = utils.create_user()
        self.category = utils.create_category()
        self.topic = utils.create_topic(category=self.category, user=self.user)

    def tearDown(self):
        media_test = os.path.join(settings.BASE_DIR, 'media_test')
        shutil.rmtree(media_test, ignore_errors=True)

    @override_settings(ST_TESTS_RATELIMIT_NEVER_EXPIRE=True)
    def test_comment_publish(self):
        """
        create comment
        """
        utils.login(self)
        form_data = {'comment': 'foobar'}
        response = self.client.post(
            reverse('spirit:comment:publish', kwargs={'topic_id': self.topic.pk}),
            form_data)
        comment = Comment.objects.all().order_by('-pk').last()
        expected_url = reverse('spirit:comment:find', kwargs={'pk': comment.pk})
        self.assertRedirects(
            response, expected_url, status_code=302, target_status_code=302)
        self.assertEqual(len(Comment.objects.all()), 1)

        # ratelimit
        self.client.post(
            reverse('spirit:comment:publish', kwargs={'topic_id': self.topic.pk}),
            form_data)
        self.assertEqual(len(Comment.objects.all()), 1)

        # get
        response = self.client.get(reverse(
            'spirit:comment:publish', kwargs={'topic_id': self.topic.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['topic'], self.topic)

    def test_comment_publish_comment_posted(self):
        """
        Should call comment_posted
        """
        res = []

        def mocked_comment_posted(comment, mentions):
            res.append(comment)
            res.append(mentions)

        org_comment_posted, views.comment_posted = (
            views.comment_posted, mocked_comment_posted)
        try:
            utils.login(self)
            form_data = {'comment': 'foobar'}
            self.client.post(
                reverse('spirit:comment:publish', kwargs={'topic_id': self.topic.pk}),
                form_data)
            self.assertEqual(len(Comment.objects.all()), 1)
            self.assertEqual(res[0], Comment.objects.first())
            self.assertEqual(res[1], {})
        finally:
            views.comment_posted = org_comment_posted

    @override_settings(ST_DOUBLE_POST_THRESHOLD_MINUTES=10)
    def test_comment_publish_double_post(self):
        """
        Should prevent double posts
        """
        utils.login(self)
        comment_txt = 'foobar'
        utils.create_comment(topic=self.topic)
        self.assertEqual(len(Comment.objects.all()), 1)

        # First post
        self.client.post(
            reverse('spirit:comment:publish', kwargs={'topic_id': self.topic.pk}),
            {'comment': comment_txt})
        self.assertEqual(len(Comment.objects.all()), 2)

        # Double post
        utils.cache_clear()  # Clear rate limit
        response = self.client.post(
            reverse('spirit:comment:publish', kwargs={'topic_id': self.topic.pk}),
            {'comment': comment_txt})
        self.assertEqual(len(Comment.objects.all()), 2)  # Prevented!

        self.assertRedirects(
            response,
            expected_url=Comment.get_last_for_topic(self.topic.pk).get_absolute_url(),
            status_code=302,
            target_status_code=302)

        # New post
        utils.cache_clear()  # Clear rate limit
        self.client.post(
            reverse('spirit:comment:publish', kwargs={'topic_id': self.topic.pk}),
            {'comment': 'not a foobar'})
        self.assertEqual(len(Comment.objects.all()), 3)

    @override_settings(ST_DOUBLE_POST_THRESHOLD_MINUTES=10)
    def test_comment_publish_same_post_into_another_topic(self):
        """
        Should not prevent from posting the same comment into another topic
        """
        utils.login(self)
        topic_another = utils.create_topic(category=self.topic.category)
        comment_txt = 'foobar'

        self.client.post(
            reverse('spirit:comment:publish', kwargs={'topic_id': self.topic.pk}),
            {'comment': comment_txt})
        self.assertEqual(len(Comment.objects.all()), 1)

        utils.cache_clear()  # Clear rate limit
        self.client.post(
            reverse('spirit:comment:publish', kwargs={'topic_id': topic_another.pk}),
            {'comment': comment_txt})
        self.assertEqual(len(Comment.objects.all()), 2)

    def test_comment_publish_on_private(self):
        """
        create comment on private topic
        """
        private = utils.create_private_topic(user=self.user)

        utils.login(self)
        form_data = {'comment': 'foobar'}
        response = self.client.post(
            reverse('spirit:comment:publish', kwargs={'topic_id': private.topic.pk}),
            form_data)
        comment = Comment.objects.all().order_by('-pk').last()
        expected_url = reverse('spirit:comment:find', kwargs={'pk': comment.pk, })
        self.assertRedirects(
            response, expected_url, status_code=302, target_status_code=302)
        self.assertEqual(len(Comment.objects.all()), 1)

    def test_comment_publish_on_closed_topic(self):
        """
        should not be able to create a comment on a closed topic
        """
        Topic.objects.filter(pk=self.topic.pk).update(is_closed=True)

        utils.login(self)
        form_data = {'comment': 'foobar'}
        response = self.client.post(
            reverse('spirit:comment:publish', kwargs={'topic_id': self.topic.pk}),
            form_data)
        self.assertEqual(response.status_code, 404)

    def test_comment_publish_on_closed_category(self):
        """
        should be able to create a comment on a closed category (if topic is not closed)
        """
        Category.objects.filter(pk=self.category.pk).update(is_closed=True)

        utils.login(self)
        form_data = {'comment': 'foobar'}
        response = self.client.post(
            reverse('spirit:comment:publish', kwargs={'topic_id': self.topic.pk}),
            form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(Comment.objects.all()), 1)

    def test_comment_publish_on_removed_topic_or_category(self):
        """
        should not be able to create a comment
        """
        # removed category
        Category.objects.all().update(is_removed=True)

        utils.login(self)
        form_data = {'comment': 'foobar'}
        response = self.client.post(
            reverse('spirit:comment:publish', kwargs={'topic_id': self.topic.pk}),
            form_data)
        self.assertEqual(response.status_code, 404)

        # removed subcategory
        Category.objects.all().update(is_removed=False)
        subcategory = utils.create_category(parent=self.category, is_removed=True)
        topic2 = utils.create_topic(subcategory)

        utils.login(self)
        form_data = {'comment': 'foobar'}
        response = self.client.post(
            reverse('spirit:comment:publish', kwargs={'topic_id': topic2.pk}),
            form_data)
        self.assertEqual(response.status_code, 404)

        # removed topic
        Category.objects.all().update(is_removed=False)
        Topic.objects.all().update(is_removed=True)

        utils.login(self)
        form_data = {'comment': 'foobar'}
        response = self.client.post(
            reverse('spirit:comment:publish', kwargs={'topic_id': self.topic.pk}),
            form_data)
        self.assertEqual(response.status_code, 404)

    def test_comment_publish_no_access(self):
        """
        should not be able to create a comment on a private topic if has no access
        """
        private = utils.create_private_topic(user=self.user)
        private.delete()

        utils.login(self)
        form_data = {'comment': 'foobar'}
        response = self.client.post(
            reverse('spirit:comment:publish', kwargs={'topic_id': private.topic.pk}),
            form_data)
        self.assertEqual(response.status_code, 404)

    def test_comment_publish_quote(self):
        """
        create comment quote
        """
        utils.login(self)
        comment = utils.create_comment(topic=self.topic)
        response = self.client.get(
            reverse('spirit:comment:publish', kwargs={
                'topic_id': self.topic.pk,
                'pk': comment.pk}))
        self.assertEqual(
            response.context['form'].initial['comment'],
            markdown.quotify(comment.comment, comment.user.username))

    def test_comment_publish_next(self):
        """
        next on create comment
        """
        utils.login(self)
        form_data = {'comment': 'foobar', 'next': '/fakepath/'}
        response = self.client.post(
            reverse('spirit:comment:publish', kwargs={'topic_id': self.topic.pk, }),
            form_data)
        self.assertRedirects(response, '/fakepath/', status_code=302, target_status_code=404)

    def test_comment_update(self):
        """
        update comment
        """
        comment = utils.create_comment(user=self.user, topic=self.topic)

        utils.login(self)
        form_data = {'comment': 'barfoo', }
        response = self.client.post(
            reverse('spirit:comment:update', kwargs={'pk': comment.pk}),
            form_data)
        expected_url = reverse('spirit:comment:find', kwargs={'pk': comment.pk, })
        self.assertRedirects(response, expected_url, status_code=302, target_status_code=302)
        self.assertEqual(Comment.objects.get(pk=comment.pk).comment, 'barfoo')

        # next
        form_data.update({'next': '/fakepath/'})
        response = self.client.post(
            reverse('spirit:comment:update', kwargs={'pk': comment.pk}),
            form_data)
        self.assertRedirects(response, '/fakepath/', status_code=302, target_status_code=404)

    def test_comment_update_not_moderator(self):
        """
        non moderators can not update other people comments
        """
        user = utils.create_user()
        comment = utils.create_comment(user=user, topic=self.topic)

        utils.login(self)
        form_data = {'comment': 'barfoo'}
        response = self.client.post(
            reverse('spirit:comment:update', kwargs={'pk': comment.pk}),
            form_data)
        self.assertEqual(response.status_code, 404)

    def test_comment_update_moderator(self):
        """
        moderators can update other people comments
        """
        UserProfile.objects.filter(user__pk=self.user.pk).update(is_moderator=True)
        user = utils.create_user()
        comment = utils.create_comment(user=user, topic=self.topic)

        utils.login(self)
        form_data = {'comment': 'barfoo'}
        response = self.client.post(
            reverse('spirit:comment:update', kwargs={'pk': comment.pk}),
            form_data)
        expected_url = reverse('spirit:comment:find', kwargs={'pk': comment.pk})
        self.assertRedirects(
            response, expected_url, status_code=302, target_status_code=302)
        self.assertEqual(Comment.objects.get(pk=comment.pk).comment, 'barfoo')

    def test_comment_update_moderator_private(self):
        """
        moderators can not update comments in private topics they has no access
        """
        UserProfile.objects.filter(user__pk=self.user.pk).update(is_moderator=True)
        user = utils.create_user()
        topic_private = utils.create_private_topic()
        comment = utils.create_comment(user=user, topic=topic_private.topic)

        utils.login(self)
        form_data = {'comment': 'barfoo'}
        response = self.client.post(
            reverse('spirit:comment:update', kwargs={'pk': comment.pk}),
            form_data)
        self.assertEqual(response.status_code, 404)

    def test_comment_update_increase_modified_count(self):
        """
        Should increase the modified count after an update
        """
        utils.login(self)
        comment_posted = utils.create_comment(user=self.user, topic=self.topic)
        form_data = {'comment': 'my comment, oh!'}
        self.client.post(
            reverse('spirit:comment:update', kwargs={'pk': comment_posted.pk}),
            form_data)
        self.assertEqual(Comment.objects.get(pk=comment_posted.pk).modified_count, 1)

    def test_comment_update_history(self):
        """
        Should add the *first* and *modified* comments to the history
        """
        utils.login(self)
        comment_posted = utils.create_comment(user=self.user, topic=self.topic)
        form_data = {'comment': 'my comment, oh!'}
        self.client.post(
            reverse('spirit:comment:update', kwargs={'pk': comment_posted.pk}),
            form_data)
        comments_history = CommentHistory.objects.filter(comment_fk=comment_posted).order_by('pk')
        self.assertEqual(len(comments_history), 2)  # first and edited
        self.assertIn(comment_posted.comment_html, comments_history[0].comment_html)  # first
        self.assertIn('my comment, oh!', comments_history[1].comment_html)  # modified

    def test_comment_delete_permission_denied_to_non_moderator(self):
        req = RequestFactory().get('/')
        req.user = self.user
        req.user.st.is_moderator = False
        self.assertRaises(PermissionDenied, comment_delete, req)

    def test_comment_delete(self):
        """
        comment delete
        """
        self.user = utils.create_user()
        self.user.st.is_moderator = True
        self.user.st.save()
        comment = utils.create_comment(user=self.user, topic=self.topic)

        utils.login(self)
        form_data = {}
        response = self.client.post(
            reverse('spirit:comment:delete', kwargs={'pk': comment.pk}),
            form_data)
        expected_url = comment.get_absolute_url()
        self.assertRedirects(
            response, expected_url, status_code=302, target_status_code=302)

        response = self.client.get(reverse(
            'spirit:comment:delete', kwargs={'pk': comment.pk}))
        self.assertEqual(response.status_code, 200)

    def test_comment_undelete(self):
        """
        comment undelete
        """
        self.user = utils.create_user()
        self.user.st.is_moderator = True
        self.user.st.save()
        comment = utils.create_comment(user=self.user, topic=self.topic, is_removed=True)

        utils.login(self)
        form_data = {}
        response = self.client.post(
            reverse('spirit:comment:undelete', kwargs={'pk': comment.pk}),
            form_data)
        expected_url = comment.get_absolute_url()
        self.assertRedirects(
            response, expected_url, status_code=302, target_status_code=302)

        response = self.client.get(reverse(
            'spirit:comment:undelete', kwargs={'pk': comment.pk}))
        self.assertEqual(response.status_code, 200)

    def test_comment_move(self):
        """
        comment move to another topic
        """
        utils.login(self)
        self.user.st.is_moderator = True
        self.user.save()
        Topic.objects.filter(pk=self.topic.pk).update(comment_count=2)
        comment = utils.create_comment(user=self.user, topic=self.topic)
        comment2 = utils.create_comment(user=self.user, topic=self.topic)
        to_topic = utils.create_topic(category=self.category)
        form_data = {
            'topic': to_topic.pk,
            'comments': [comment.pk, comment2.pk], }
        response = self.client.post(
            reverse('spirit:comment:move', kwargs={'topic_id': self.topic.pk}),
            form_data)
        expected_url = self.topic.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302)
        self.assertEqual(Comment.objects.filter(topic=to_topic.pk).count(), 2)
        self.assertEqual(Comment.objects.filter(topic=self.topic.pk).count(), 0)
        self.assertEqual(Topic.objects.get(pk=self.topic.pk).comment_count, 0)

    def test_comment_find(self):
        """
        comment absolute and lazy url
        """
        comment = utils.create_comment(user=self.user, topic=self.topic)
        response = self.client.post(
            reverse('spirit:comment:find', kwargs={'pk': comment.pk}))
        expected_url = comment.topic.get_absolute_url() + "#c1"
        self.assertRedirects(response, expected_url, status_code=302)

    @override_settings(
        MEDIA_ROOT=os.path.join(settings.BASE_DIR, 'media_test'),
        ST_PREVENT_SOME_FILE_DUPLICATION=True)
    def test_comment_image_upload(self):
        """
        comment image upload
        """
        utils.login(self)
        img = io.BytesIO(
            b'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00'
            b'\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')
        files = {'image': SimpleUploadedFile(
            'image.gif', img.read(), content_type='image/gif')}
        response = self.client.post(
            reverse('spirit:comment:image-upload-ajax'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            data=files)
        res = json.loads(response.content.decode('utf-8'))
        image_url = os.path.join(
            settings.MEDIA_URL, 'spirit', 'images', str(self.user.pk),
            "bf21c3043d749d5598366c26e7e4ab44.gif"
        ).replace("\\", "/")
        self.assertEqual(res['url'], image_url)
        image_path = os.path.join(
            settings.MEDIA_ROOT, 'spirit', 'images', str(self.user.pk),
            "bf21c3043d749d5598366c26e7e4ab44.gif")
        self.assertTrue(os.path.isfile(image_path))
        shutil.rmtree(settings.MEDIA_ROOT)  # cleanup

    @override_settings(MEDIA_ROOT=os.path.join(settings.BASE_DIR, 'media_test'))
    def test_comment_image_upload_unique(self):
        user_images_parts = ('spirit', 'images', str(self.user.pk))
        user_images_base = os.path.join(*user_images_parts)
        user_media = os.path.join(settings.MEDIA_ROOT, user_images_base)
        self.assertFalse(os.path.isdir(user_media))

        utils.login(self)
        img = io.BytesIO(
            b'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00'
            b'\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')
        image_name = 'foo_image.gif'
        file = SimpleUploadedFile(
            image_name, img.read(), content_type='image/gif')
        response = self.client.post(
            reverse('spirit:comment:image-upload-ajax'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            data={'image': file})
        res = json.loads(response.content.decode('utf-8'))

        self.assertTrue(os.path.isdir(user_media))

        url_parts = res['url'].split('/')
        self.assertEqual(
            url_parts[:-2],
            (settings.MEDIA_URL + '/'.join(user_images_parts)).split('/'))
        self.assertEqual(len(url_parts[-2]), 32)  # uuid
        self.assertEqual(url_parts[-1], image_name)

        self.assertEqual(len(os.listdir(user_media)), 1)
        self.assertTrue(os.path.join(
            user_media, os.listdir(user_media)[0], image_name))
        shutil.rmtree(settings.MEDIA_ROOT)  # cleanup

    @override_settings(MEDIA_ROOT=os.path.join(settings.BASE_DIR, 'media_test'))
    def test_comment_image_upload_unique_no_duplication(self):
        utils.login(self)
        img = io.BytesIO(
            b'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00'
            b'\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')
        image_name = 'foo_image.gif'
        file = SimpleUploadedFile(
            image_name, img.read(), content_type='image/gif')

        response = self.client.post(
            reverse('spirit:comment:image-upload-ajax'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            data={'image': file})
        res = json.loads(response.content.decode('utf-8'))
        first_url = res['url']

        utils.cache_clear()
        file.seek(0)
        response = self.client.post(
            reverse('spirit:comment:image-upload-ajax'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            data={'image': file})
        res = json.loads(response.content.decode('utf-8'))
        second_url = res['url']

        self.assertNotEqual(first_url, second_url)

    @override_settings(MEDIA_ROOT=os.path.join(settings.BASE_DIR, 'media_test'))
    def test_comment_image_upload_mixed_case_ext(self):
        utils.login(self)
        img = io.BytesIO(
            b'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00'
            b'\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')
        image_name = 'foo_image.GiF'
        file = SimpleUploadedFile(
            image_name, img.read(), content_type='image/gif')
        response = self.client.post(
            reverse('spirit:comment:image-upload-ajax'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            data={'image': file})
        res = json.loads(response.content.decode('utf-8'))
        self.assertTrue(res['url'].endswith('/foo_image.gif'))

    @override_settings(MEDIA_ROOT=os.path.join(settings.BASE_DIR, 'media_test'))
    def test_comment_image_upload_unique_no_name(self):
        utils.login(self)
        img = io.BytesIO(
            b'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00'
            b'\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')
        image_name = '.gif'
        file = SimpleUploadedFile(
            image_name, img.read(), content_type='image/gif')
        response = self.client.post(
            reverse('spirit:comment:image-upload-ajax'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            data={'image': file})
        res = json.loads(response.content.decode('utf-8'))
        # django 2.2 and 3.0 compat
        self.assertTrue(
            'File extension “” is not allowed' in res['error']['image'][0]
            or 'File extension \'\' is not allowed' in res['error']['image'][0])

    @override_settings(
        MEDIA_ROOT=os.path.join(settings.BASE_DIR, 'media_test'),
        ST_PREVENT_SOME_FILE_DUPLICATION=False)
    def test_comment_image_upload_unique_bad_name(self):
        utils.login(self)
        img = io.BytesIO(
            b'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00'
            b'\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')
        ext = '.gif'
        image_name = '???' + ext
        file = SimpleUploadedFile(
            image_name, img.read(), content_type='image/gif')
        response = self.client.post(
            reverse('spirit:comment:image-upload-ajax'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            data={'image': file})
        res = json.loads(response.content.decode('utf-8'))
        self.assertTrue(res['url'].endswith(ext))
        self.assertTrue(len(os.path.basename(res['url'])), len(ext) + 32)  # uuid name

    @override_settings(
        MEDIA_ROOT=os.path.join(settings.BASE_DIR, 'media_test'),
        ST_PREVENT_SOME_FILE_DUPLICATION=False)
    def test_comment_image_upload_unique_dots_name(self):
        utils.login(self)
        img = io.BytesIO(
            b'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00'
            b'\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')
        ext = '.gif'
        image_name = '?...?...?' + ext
        file = SimpleUploadedFile(
            image_name, img.read(), content_type='image/gif')
        response = self.client.post(
            reverse('spirit:comment:image-upload-ajax'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            data={'image': file})
        res = json.loads(response.content.decode('utf-8'))
        self.assertTrue(res['url'].endswith(ext))
        self.assertTrue(len(os.path.basename(res['url'])), len(ext) + 32)  # uuid name

    @override_settings(
        MEDIA_ROOT=os.path.join(settings.BASE_DIR, 'media_test'),
        ST_PREVENT_SOME_FILE_DUPLICATION=False)
    def test_comment_image_upload_unique_hidden_name(self):
        utils.login(self)
        img = io.BytesIO(
            b'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00'
            b'\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')
        ext = '.gif'
        image_name = '?.h?i?d?d?e?n' + ext
        file = SimpleUploadedFile(
            image_name, img.read(), content_type='image/gif')
        response = self.client.post(
            reverse('spirit:comment:image-upload-ajax'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            data={'image': file})
        res = json.loads(response.content.decode('utf-8'))
        self.assertTrue(res['url'].endswith('/hidden.gif'))

    def test_comment_image_upload_invalid(self):
        """
        comment image upload, invalid image
        """
        utils.login(self)
        image = io.BytesIO(b'BAD\x02D\x01\x00;')
        image.name = 'image.gif'
        image.content_type = 'image/gif'
        files = {'image': SimpleUploadedFile(image.name, image.read())}
        response = self.client.post(
            reverse('spirit:comment:image-upload-ajax'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            data=files)
        res = json.loads(response.content.decode('utf-8'))
        self.assertIn('error', res.keys())
        self.assertIn('image', res['error'].keys())

    @utils.with_test_storage
    def test_comment_image_upload_spirit_storage(self):
        utils.clean_media()
        utils.login(self)
        content = (
            b'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00'
            b'\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')
        file = SimpleUploadedFile('image.gif', content)
        response = self.client.post(
            reverse('spirit:comment:image-upload-ajax'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            data={'image': file})
        res = json.loads(response.content.decode('utf-8'))
        self.assertTrue(res['url'].endswith('/image_test.gif'))

    @skipIf(not settings.ST_UPLOAD_FILE_ENABLED, 'No magic file support')
    @override_settings(
        MEDIA_ROOT=os.path.join(settings.BASE_DIR, 'media_test'),
        FILE_UPLOAD_MAX_MEMORY_SIZE=2621440,
        ST_PREVENT_SOME_FILE_DUPLICATION=True)
    def test_comment_file_upload(self):
        """
        Check (in-memory) upload files are checked
        """
        utils.login(self)

        # sample valid pdf - https://stackoverflow.com/a/17280876
        file = io.BytesIO(
            b'%PDF-1.0\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1'
            b'>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 3 3]>>endobj\nxref\n0 4\n0000000000 65535 f\n000000'
            b'0010 00000 n\n0000000053 00000 n\n0000000102 00000 n\ntrailer<</Size 4/Root 1 0 R>>\nstartxre'
            b'f\n149\n%EOF\n')
        files = {'file': SimpleUploadedFile(
            'file.pdf', file.read(), content_type='application/pdf')}
        response = self.client.post(
            reverse('spirit:comment:file-upload-ajax'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            data=files)

        res = json.loads(response.content.decode('utf-8'))
        file_url = os.path.join(
            settings.MEDIA_URL, 'spirit', 'files', str(self.user.pk),  "fadcb2389bb2b69b46bc54185de0ae91.pdf"
        ).replace("\\", "/")
        self.assertEqual(res['url'], file_url)
        file_path = os.path.join(
            settings.MEDIA_ROOT, 'spirit', 'files', str(self.user.pk), "fadcb2389bb2b69b46bc54185de0ae91.pdf")

        with open(file_path, 'rb') as fh:
            file.seek(0)
            self.assertEqual(fh.read(), file.read())

        shutil.rmtree(settings.MEDIA_ROOT)  # cleanup

    @skipIf(not settings.ST_UPLOAD_FILE_ENABLED, 'No magic file support')
    @override_settings(
        MEDIA_ROOT=os.path.join(settings.BASE_DIR, 'media_test'),
        FILE_UPLOAD_MAX_MEMORY_SIZE=1,
        ST_PREVENT_SOME_FILE_DUPLICATION=True)
    def test_comment_file_upload_tmp_file(self):
        """
        Check (tmp) upload files are checked
        """
        utils.login(self)
        file = io.BytesIO(
            b'%PDF-1.0\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1'
            b'>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 3 3]>>endobj\nxref\n0 4\n0000000000 65535 f\n000000'
            b'0010 00000 n\n0000000053 00000 n\n0000000102 00000 n\ntrailer<</Size 4/Root 1 0 R>>\nstartxre'
            b'f\n149\n%EOF\n')
        files = {
            'file': SimpleUploadedFile(
                'file_large.pdf', file.read(), content_type='application/pdf')}
        response = self.client.post(
            reverse('spirit:comment:file-upload-ajax'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            data=files)

        res = json.loads(response.content.decode('utf-8'))
        file_url = os.path.join(
            settings.MEDIA_URL, 'spirit', 'files', str(self.user.pk), "fadcb2389bb2b69b46bc54185de0ae91.pdf"
        ).replace("\\", "/")
        self.assertEqual(res['url'], file_url)
        file_path = os.path.join(
            settings.MEDIA_ROOT, 'spirit', 'files', str(self.user.pk), "fadcb2389bb2b69b46bc54185de0ae91.pdf")

        with open(file_path, 'rb') as fh:
            file.seek(0)
            self.assertEqual(fh.read(), file.read())

        shutil.rmtree(settings.MEDIA_ROOT)  # cleanup

    @skipIf(not settings.ST_UPLOAD_FILE_ENABLED, 'No magic file support')
    @override_settings(MEDIA_ROOT=os.path.join(settings.BASE_DIR, 'media_test'))
    def test_comment_file_upload_unique(self):
        user_files_parts = ('spirit', 'files', str(self.user.pk))
        user_files_base = os.path.join(*user_files_parts)
        user_media = os.path.join(settings.MEDIA_ROOT, user_files_base)
        self.assertFalse(os.path.isdir(user_media))

        utils.login(self)
        pdf = io.BytesIO(
            b'%PDF-1.0\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1'
            b'>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 3 3]>>endobj\nxref\n0 4\n0000000000 65535 f\n000000'
            b'0010 00000 n\n0000000053 00000 n\n0000000102 00000 n\ntrailer<</Size 4/Root 1 0 R>>\nstartxre'
            b'f\n149\n%EOF\n')
        file_name = 'foo.pdf'
        file = SimpleUploadedFile(
            file_name, pdf.read(), content_type='application/pdf')
        response = self.client.post(
            reverse('spirit:comment:file-upload-ajax'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            data={'file': file})
        res = json.loads(response.content.decode('utf-8'))

        self.assertTrue(os.path.isdir(user_media))

        url_parts = res['url'].split('/')
        self.assertEqual(
            url_parts[:-2],
            (settings.MEDIA_URL + '/'.join(user_files_parts)).split('/'))
        self.assertEqual(len(url_parts[-2]), 32)  # uuid
        self.assertEqual(url_parts[-1], file_name)

        self.assertEqual(len(os.listdir(user_media)), 1)
        self.assertTrue(os.path.join(
            user_media, os.listdir(user_media)[0], file_name))
        shutil.rmtree(settings.MEDIA_ROOT)  # cleanup

    @skipIf(not settings.ST_UPLOAD_FILE_ENABLED, 'No magic file support')
    @override_settings(MEDIA_ROOT=os.path.join(settings.BASE_DIR, 'media_test'))
    def test_comment_file_upload_unique_no_duplication(self):
        utils.login(self)
        pdf = io.BytesIO(
            b'%PDF-1.0\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1'
            b'>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 3 3]>>endobj\nxref\n0 4\n0000000000 65535 f\n000000'
            b'0010 00000 n\n0000000053 00000 n\n0000000102 00000 n\ntrailer<</Size 4/Root 1 0 R>>\nstartxre'
            b'f\n149\n%EOF\n')
        file_name = 'foo.pdf'
        file = SimpleUploadedFile(
            file_name, pdf.read(), content_type='application/pdf')

        response = self.client.post(
            reverse('spirit:comment:file-upload-ajax'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            data={'file': file})
        res = json.loads(response.content.decode('utf-8'))
        first_url = res['url']

        utils.cache_clear()
        file.seek(0)
        response = self.client.post(
            reverse('spirit:comment:file-upload-ajax'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            data={'file': file})
        res = json.loads(response.content.decode('utf-8'))
        second_url = res['url']

        self.assertNotEqual(first_url, second_url)

    @skipIf(not settings.ST_UPLOAD_FILE_ENABLED, 'No magic file support')
    def test_comment_file_upload_invalid_ext(self):
        """
        comment file upload, invalid file extension
        """
        utils.login(self)
        # sample valid pdf - https://stackoverflow.com/a/17280876
        file = io.BytesIO(
            b'%PDF-1.0\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1'
            b'>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 3 3]>>endobj\nxref\n0 4\n0000000000 65535 f\n000000'
            b'0010 00000 n\n0000000053 00000 n\n0000000102 00000 n\ntrailer<</Size 4/Root 1 0 R>>\nstartxre'
            b'f\n149\n%EOF\n')
        files = {'file': SimpleUploadedFile(
            'fake.gif', file.read(), content_type='application/pdf')}
        response = self.client.post(
            reverse('spirit:comment:file-upload-ajax'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            data=files)
        res = json.loads(response.content.decode('utf-8'))
        self.assertIn('error', res)
        self.assertIn('file', res['error'])
        self.assertEqual(
            res['error']['file'],
            ['Unsupported file extension gif. Supported extensions are doc, docx, pdf.'])

    @skipIf(not settings.ST_UPLOAD_FILE_ENABLED, 'No magic file support')
    def test_comment_file_upload_invalid_mime(self):
        """
        comment file upload, invalid mime type
        """
        utils.login(self)
        file = io.BytesIO(b'BAD\x02D\x01\x00;')
        files = {
            'file': SimpleUploadedFile(
                'file.pdf', file.read(), content_type='application/pdf')}
        response = self.client.post(
            reverse('spirit:comment:file-upload-ajax'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            data=files)
        res = json.loads(response.content.decode('utf-8'))
        self.assertIn('error', res)
        self.assertIn('file', res['error'])
        self.assertEqual(
            res['error']['file'],
            ['Unsupported file mime type application/octet-stream. '
             'Supported types are application/msword, '
             'application/pdf, '
             'application/vnd.openxmlformats-officedocument.wordprocessingml.document.'])


class CommentModelsTest(TestCase):

    def setUp(self):
        utils.cache_clear()
        self.user = utils.create_user()
        self.category = utils.create_category()
        self.topic = utils.create_topic(category=self.category, user=self.user)

    def test_comment_increase_modified_count(self):
        """
        Increase modified_count
        """
        comment = utils.create_comment(topic=self.topic)
        comment.increase_modified_count()
        self.assertEqual(Comment.objects.get(pk=comment.pk).modified_count, 1)

    def test_comment_increase_likes_count(self):
        """
        Increase like_count on comment like
        """
        comment = utils.create_comment(topic=self.topic)
        comment.increase_likes_count()
        self.assertEqual(Comment.objects.get(pk=comment.pk).likes_count, 1)

    def test_comment_decrease_likes_count(self):
        """
        Decrease like_count on remove comment like
        """
        comment = utils.create_comment(topic=self.topic, likes_count=1)
        comment.decrease_likes_count()
        self.assertEqual(Comment.objects.get(pk=comment.pk).likes_count, 0)

    def test_comment_create_moderation_action(self):
        """
        Create comment that tells what moderation action was made
        """
        Comment.create_moderation_action(user=self.user, topic=self.topic, action=1)
        self.assertEqual(Comment.objects.filter(
            user=self.user, topic=self.topic, action=1).count(), 1)

    def test_comment_get_last_for_topic(self):
        """
        Should return last comment for a given topic
        """
        utils.create_comment(topic=self.topic)
        comment_last = utils.create_comment(topic=self.topic)
        self.assertEqual(Comment.get_last_for_topic(self.topic.pk), comment_last)


class CommentTemplateTagTests(TestCase):

    def setUp(self):
        utils.cache_clear()
        self.user = utils.create_user()
        self.category = utils.create_category()
        self.topic = utils.create_topic(category=self.category, user=self.user)
        utils.create_comment(topic=self.topic)
        utils.create_comment(topic=self.topic)
        utils.create_comment(topic=self.topic)

    def test_render_comments_form(self):
        """
        should display simple comment form
        """
        req = RequestFactory().get('/')
        req.user = self.user
        req_context = Context({'topic': self.topic, 'request': req})
        Template(
            "{% load spirit_tags %}"
            "{% render_comments_form topic %}"
        ).render(req_context)
        context = render_comments_form(req_context, self.topic)
        self.assertEqual(context['next'], None)
        self.assertIsInstance(context['form'], CommentForm)
        self.assertEqual(context['topic_id'], self.topic.pk)

    def test_get_action_text(self):
        """
        should display action
        """
        comment = utils.create_comment(topic=self.topic)
        comment.action = Comment.CLOSED
        out = Template(
            "{% load spirit_tags %}"
            "{% get_comment_action_text comment %}"
        ).render(Context({'comment': comment}))
        self.assertNotEqual(out, "")
        self.assertIn(comment.user.st.nickname, out)
        self.assertIn("closed this", out)


class CommentFormTest(TestCase):

    def setUp(self):
        utils.cache_clear()
        self.user = utils.create_user()
        self.category = utils.create_category()
        self.topic = utils.create_topic(category=self.category)

    def test_comment_create(self):
        form_data = {'comment': 'foo', }
        form = CommentForm(data=form_data)
        self.assertEqual(form.is_valid(), True)

    def test_comment_markdown(self):
        form_data = {
            'comment': '**Spirit unicode: áéíóú** <script>alert();</script>'}
        form = CommentForm(data=form_data)
        self.assertEqual(form.is_valid(), True)
        form.user = self.user
        form.topic = self.topic
        comment = form.save()
        self.assertEqual(
            comment.comment_html,
            '<p><strong>Spirit unicode: áéíóú</strong> '
            '&lt;script&gt;alert();&lt;/script&gt;</p>')

    def test_comment_markdown_no_follow(self):
        form_data = {'comment': 'http://foo.com'}
        form = CommentForm(data=form_data)
        self.assertEqual(form.is_valid(), True)
        form.user = self.user
        form.topic = self.topic
        comment = form.save()
        self.assertEqual(
            comment.comment_html,
            '<p><a rel="nofollow" href="http://foo.com">http://foo.com</a></p>')

        self.user.st.is_moderator = True
        comment2 = form.save()
        self.assertEqual(
            comment2.comment_html,
            '<p><a rel="nofollow" href="http://foo.com">http://foo.com</a></p>')

    def test_comment_get_comment_hash(self):
        """
        Should return the comment hash
        """
        comment_txt = 'foo'
        form_data = {'comment': comment_txt}
        form = CommentForm(data=form_data, topic=self.topic)
        self.assertTrue(form.is_valid())

        comment_txt_to_hash = '{}thread-{}'.format(comment_txt, self.topic.pk)
        self.assertEqual(
            form.get_comment_hash(),
            hashlib.md5(comment_txt_to_hash.encode('utf-8')).hexdigest())

    def test_comment_get_comment_hash_from_field(self):
        """
        Should return the comment hash from field
        """
        comment_hash = '1' * 32
        form_data = {'comment': 'foo', 'comment_hash': comment_hash}
        form = CommentForm(data=form_data, topic=self.topic)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.get_comment_hash(), comment_hash)

    def test_comments_move(self):
        comment = utils.create_comment(user=self.user, topic=self.topic)
        comment2 = utils.create_comment(user=self.user, topic=self.topic)
        to_topic = utils.create_topic(category=self.category)
        form_data = {
            'topic': to_topic.pk,
            'comments': [comment.pk, comment2.pk], }
        form = CommentMoveForm(topic=self.topic, data=form_data)
        self.assertEqual(form.is_valid(), True)
        self.assertEqual(form.save(), list(Comment.objects.filter(topic=to_topic)))

    @override_settings(ST_PREVENT_SOME_FILE_DUPLICATION=True)
    def test_comment_image_upload(self):
        """
        Image upload
        """
        content = (
            b'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00'
            b'\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')
        img = io.BytesIO(content)
        files = {
            'image': SimpleUploadedFile(
                'image.gif', img.read(), content_type='image/gif')}

        form = CommentImageForm(user=self.user, data={}, files=files)
        self.assertTrue(form.is_valid())
        image = form.save()
        self.assertEqual(image.name, "bf21c3043d749d5598366c26e7e4ab44.gif")
        image_url = os.path.join(
            settings.MEDIA_URL, 'spirit', 'images', str(self.user.pk),
            image.name).replace("\\", "/")
        self.assertEqual(image.url, image_url)
        image_path = os.path.join(
            settings.MEDIA_ROOT, 'spirit', 'images', str(self.user.pk), image.name)
        self.assertTrue(os.path.isfile(image_path))

        with open(image_path, "rb") as fh:
            self.assertEqual(fh.read(), content)

        os.remove(image_path)

    def test_comment_image_upload_ext_ci(self):
        """Should allow images with mixed case extension"""
        content = (
            b'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00'
            b'\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')
        files = {
            'image': SimpleUploadedFile(
                'image.GiF', content, content_type='image/gif')}
        form = CommentImageForm(user=self.user, data={}, files=files)
        self.assertTrue(form.is_valid())

    def test_comment_image_upload_no_extension(self):
        """
        Image upload without extension should raise an error
        """
        img = io.BytesIO(
            b'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00'
            b'\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')
        files = {'image': SimpleUploadedFile(
            'image', img.read(), content_type='image/gif')}
        form = CommentImageForm(user=self.user, data={}, files=files)
        self.assertFalse(form.is_valid())

    def test_comment_image_upload_not_allowed_ext(self):
        """
        Image upload with good mime but not allowed extension should raise an error
        """
        img = io.BytesIO(
            b'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00'
            b'\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')
        files = {'image': SimpleUploadedFile(
            'image.png', img.read(), content_type='image/png')}
        form = CommentImageForm(user=self.user, data={}, files=files)
        self.assertFalse(form.is_valid())

    @override_settings(ST_ALLOWED_UPLOAD_IMAGE_FORMAT=['png', ])
    def test_comment_image_upload_not_allowed_format(self):
        """
        Image upload without allowed mime but good extension should raise an error
        """
        img = io.BytesIO(
            b'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00'
            b'\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')
        # fake png extension
        files = {'image': SimpleUploadedFile(
            'image.png', img.read(), content_type='image/png')}
        form = CommentImageForm(data={}, files=files)
        self.assertFalse(form.is_valid())

    def test_comment_image_upload_invalid(self):
        """
        Image upload with bad content but good extension should raise an error
        """
        img = io.BytesIO(b'bad\x00;')
        files = {'image': SimpleUploadedFile(
            'image.gif', img.read(), content_type='image/gif')}
        form = CommentImageForm(data={}, files=files)
        self.assertFalse(form.is_valid())

    @utils.with_test_storage
    def test_comment_image_upload_spirit_storage(self):
        utils.clean_media()
        content = (
            b'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00'
            b'\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')
        img = io.BytesIO(content)
        files = {
            'image': SimpleUploadedFile(
                'image.gif', img.read(), content_type='image/gif')}
        form = CommentImageForm(user=self.user, data={}, files=files)
        self.assertTrue(form.is_valid())
        image = form.save()
        self.assertEqual(image.name, "image_test.gif")

    def test_comment_file_upload_no_libmagic(self):
        """
        Magic lib should be optional
        """
        utils.login(self)
        file = io.BytesIO(
            b'%PDF-1.0\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1'
            b'>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 3 3]>>endobj\nxref\n0 4\n0000000000 65535 f\n000000'
            b'0010 00000 n\n0000000053 00000 n\n0000000102 00000 n\ntrailer<</Size 4/Root 1 0 R>>\nstartxre'
            b'f\n149\n%EOF\n')
        files = {'file': SimpleUploadedFile(
            'file.pdf', file.read(), content_type='application/pdf')}
        form = CommentFileForm(data={}, files=files)

        comment_forms_magic_orig, comment_forms.magic = comment_forms.magic, None
        try:
            self.assertFalse(form.is_valid())
        finally:
            comment_forms.magic = comment_forms_magic_orig

    def test_comment_max_len(self):
        """
        Restrict comment len
        """
        comment = 'a' * settings.ST_COMMENT_MAX_LEN
        form_data = {'comment': comment}
        form = CommentForm(data=form_data)
        self.assertEqual(form.is_valid(), True)

    def test_comment_max_len_invalid(self):
        """
        Restrict comment len
        """
        comment = 'a' * (settings.ST_COMMENT_MAX_LEN + 1)
        form_data = {'comment': comment}
        form = CommentForm(data=form_data)
        self.assertEqual(form.is_valid(), False)


class CommentUtilsTest(TestCase):

    def setUp(self):
        utils.cache_clear()
        self.user = utils.create_user()
        self.category = utils.create_category()
        self.topic = utils.create_topic(category=self.category, user=self.user)

    @utils.immediate_on_commit
    @override_settings(ST_TASK_MANAGER='tests')
    def test_comment_posted(self):
        """
        * Should create subscription
        * Should notify subscribers
        * Should notify mentions
        * Should increase topic's comment counter
        * Should mark the topic as unread
        * Should notify by email
        """
        # Should create subscription
        subscriber = self.user
        comment = utils.create_comment(user=subscriber, topic=self.topic)
        comment_posted(comment=comment, mentions=None)
        self.assertEqual(len(TopicNotification.objects.all()), 1)
        self.assertTrue(TopicNotification.objects.get(
            user=subscriber, topic=self.topic).is_read)

        # Should notify subscribers
        user = utils.create_user()
        comment = utils.create_comment(user=user, topic=self.topic)
        comment_posted(comment=comment, mentions=None)
        self.assertEqual(len(TopicNotification.objects.all()), 2)
        self.assertFalse(TopicNotification.objects.get(
            user=subscriber, topic=self.topic).is_read)

        # Should notify mentions
        mentioned = utils.create_user()
        mentions = {mentioned.username: mentioned, }
        comment = utils.create_comment(user=user, topic=self.topic)
        comment_posted(comment=comment, mentions=mentions)
        self.assertEqual(TopicNotification.objects.get(
            user=mentioned, comment=comment).action, MENTION)
        self.assertFalse(TopicNotification.objects.get(
            user=mentioned, comment=comment).is_read)

        # Should mark the topic as unread
        user_unread = utils.create_user()
        topic = utils.create_topic(self.category)
        topic_unread_creator = TopicUnread.objects.create(
            user=user, topic=topic, is_read=True)
        topic_unread_subscriber = TopicUnread.objects.create(
            user=user_unread, topic=topic, is_read=True)
        comment = utils.create_comment(user=user, topic=topic)
        comment_posted(comment=comment, mentions=None)
        self.assertTrue(TopicUnread.objects.get(pk=topic_unread_creator.pk).is_read)
        self.assertFalse(TopicUnread.objects.get(pk=topic_unread_subscriber.pk).is_read)

        # Should increase topic's comment counter
        topic = utils.create_topic(self.category)
        comment = utils.create_comment(user=user, topic=topic)
        comment_posted(comment=comment, mentions=None)
        self.assertEqual(Topic.objects.get(pk=topic.pk).comment_count, 1)
        comment_posted(comment=comment, mentions=None)
        self.assertEqual(Topic.objects.get(pk=topic.pk).comment_count, 2)

        # Should notify by email
        mail.outbox.clear()
        self.assertEqual(len(mail.outbox), 0)
        topic = utils.create_topic(self.category)
        user = utils.create_user()
        comment = utils.create_comment(user=user, topic=topic)
        comment_posted(comment=comment, mentions=None)
        user.st.notify = user.st.Notify.IMMEDIATELY | user.st.Notify.REPLY
        user.st.save()
        user2 = utils.create_user()
        comment = utils.create_comment(user=user2, topic=topic)
        comment_posted(comment=comment, mentions=None)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "{user} commented on {topic}".format(
            user=comment.user.st.nickname, topic=comment.topic.title))

        mail.outbox.clear()
        self.assertEqual(len(mail.outbox), 0)
        user = utils.create_user()
        user.st.notify = user.st.Notify.IMMEDIATELY | user.st.Notify.MENTION
        user.st.save()
        topic = utils.create_topic(self.category)
        user2 = utils.create_user()
        comment = utils.create_comment(user=user2, topic=topic)
        comment_posted(comment=comment, mentions={user.username: user})
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "{user} mention you on {topic}".format(
            user=comment.user.st.nickname, topic=comment.topic.title))

    def test_pre_comment_update(self):
        """
        * Should render static polls
        * Should create comment history maybe
        """
        # Should render static polls
        comment = utils.create_comment(
            user=self.user, topic=self.topic, comment_html='<poll name=foo>')
        CommentPoll.objects.create(comment=comment, name='foo', title="my poll")
        pre_comment_update(comment=comment)
        self.assertTrue('my poll' in comment.comment_html)

        # Should create comment history maybe
        comment = utils.create_comment(user=self.user, topic=self.topic)
        pre_comment_update(comment=comment)
        self.assertEqual(len(CommentHistory.objects.filter(comment_fk=comment)), 1)
        pre_comment_update(comment=comment)
        self.assertEqual(len(CommentHistory.objects.filter(comment_fk=comment)), 1)

    def test_post_comment_update(self):
        """
        * Should increase modified count
        * Should render static polls
        * Should create comment history
        """
        # Should increase modified count
        comment = utils.create_comment(user=self.user, topic=self.topic)
        post_comment_update(comment=comment)
        self.assertEqual(Comment.objects.get(pk=comment.pk).modified_count, 1)
        post_comment_update(comment=comment)
        self.assertEqual(Comment.objects.get(pk=comment.pk).modified_count, 2)

        # Should render static polls
        comment = utils.create_comment(
            user=self.user, topic=self.topic, comment_html='<poll name=foo>')
        CommentPoll.objects.create(comment=comment, name='foo', title="my poll")
        post_comment_update(comment=comment)
        self.assertTrue('my poll' in comment.comment_html)

        # Should create comment history
        comment = utils.create_comment(user=self.user, topic=self.topic)
        post_comment_update(comment=comment)
        self.assertEqual(len(CommentHistory.objects.filter(comment_fk=comment)), 1)
        post_comment_update(comment=comment)
        self.assertEqual(len(CommentHistory.objects.filter(comment_fk=comment)), 2)
