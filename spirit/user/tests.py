# -*- coding: utf-8 -*-

import datetime
import importlib

from django.test import TestCase, RequestFactory, TransactionTestCase
from django.urls import reverse
from django.contrib.auth import get_user_model, HASH_SESSION_KEY
from django.core import mail
from django.utils.translation import gettext as _
from django.utils import timezone
from django.test.utils import override_settings
from django.contrib.auth.models import AnonymousUser
from django.apps import apps
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse

from djconfig.utils import override_djconfig

from spirit.core.tests import utils
from spirit.core.conf import settings
from spirit.core.storage import spirit_storage
from .forms import UserProfileForm, EmailChangeForm, UserForm, EmailCheckForm
from spirit.comment.like.models import CommentLike
from spirit.topic.models import Topic
from spirit.comment.models import Comment
from spirit.comment.bookmark.models import CommentBookmark
from .utils.tokens import (
    unsub_token,
    UserActivationTokenGenerator,
    UserEmailChangeTokenGenerator)
from .utils.email import send_activation_email, send_email_change_email
from . import middleware
from .models import UserProfile

data_migration_profiles = importlib.import_module(
    'spirit.user.migrations.0004_auto_20150731_2351')
data_migration_11 = importlib.import_module(
    'spirit.user.migrations.0011_auto_20181124_2320')

User = get_user_model()


class UserViewTest(TestCase):

    def setUp(self):
        utils.cache_clear()
        self.user = utils.create_user()
        self.user2 = utils.create_user()
        self.category = utils.create_category()
        self.topic = utils.create_topic(self.category, user=self.user2)
        self.topic2 = utils.create_topic(self.category)

    def test_user_views_denied_to_non_logged_users(self):
        """
        profile user's topics, comments, likes should not be seen by guests
        """
        pk = self.user.pk
        slug = self.user.st.slug

        response = self.client.get(reverse(
            'spirit:user:topics', kwargs={'pk': pk, 'slug': slug}))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse(
            'spirit:user:detail', kwargs={'pk': pk, 'slug': slug}))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse(
            'spirit:user:likes', kwargs={'pk': pk, 'slug': slug}))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('spirit:user:update'))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('spirit:user:password-change'))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('spirit:user:email-change'))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse(
            'spirit:user:email-change-confirm', kwargs={'token': "foo"}))
        self.assertEqual(response.status_code, 302)

    @override_settings(ST_CASE_INSENSITIVE_USERNAMES=True)
    def test_profile_creation_on_register_case_insensitive_user(self):
        form_data = {
            'username': 'UnIqUeFoO',
            'email': 'some@some.com',
            'email2': 'some@some.com',
            'password': 'pass'}
        response = self.client.post(
            reverse('spirit:user:auth:register'), form_data)
        expected_url = reverse('spirit:user:auth:login')
        self.assertRedirects(response, expected_url, status_code=302)
        self.assertTrue(
            UserProfile.objects.filter(
                nickname='UnIqUeFoO',
                user__username='uniquefoo'
            ).exists())
        self.assertFalse(
            UserProfile.objects.filter(nickname='uniquefoo').exists())

    @override_settings(ST_CASE_INSENSITIVE_USERNAMES=False)
    def test_profile_creation_on_register_case_insensitive_user_off(self):
        form_data = {
            'username': 'UnIqUeFoO',
            'email': 'some@some.com',
            'email2': 'some@some.com',
            'password': 'pass'}
        response = self.client.post(
            reverse('spirit:user:auth:register'), form_data)
        expected_url = reverse('spirit:user:auth:login')
        self.assertRedirects(response, expected_url, status_code=302)
        self.assertTrue(
            UserProfile.objects.filter(
                nickname='UnIqUeFoO',
                user__username='UnIqUeFoO'
            ).exists())

    def test_profile_topics(self):
        """
        profile user's topics
        """
        utils.login(self)
        response = self.client.get(
            reverse("spirit:user:topics", kwargs={
                'pk': self.user2.pk, 'slug': self.user2.st.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['topics']), [self.topic])
        self.assertEqual(response.context['p_user'], self.user2)

    def test_profile_topics_order(self):
        """
        topics ordered by date
        """
        Topic.objects.all().delete()

        category = utils.create_category()
        topic_a = utils.create_topic(category=category, user=self.user2)
        topic_b = utils.create_topic(category=category, user=self.user2)
        topic_c = utils.create_topic(category=category, user=self.user2)

        Topic.objects.filter(pk=topic_a.pk).update(
            date=timezone.now() - datetime.timedelta(days=10))
        Topic.objects.filter(pk=topic_c.pk).update(
            date=timezone.now() - datetime.timedelta(days=5))

        utils.login(self)
        response = self.client.get(reverse(
            "spirit:user:topics", kwargs={
                'pk': self.user2.pk, 'slug': self.user2.st.slug}))
        self.assertEqual(
            list(response.context['topics']),
            [topic_b, topic_c, topic_a])

    def test_profile_topics_bookmarks(self):
        """
        profile user's topics with bookmarks
        """
        bookmark = CommentBookmark.objects.create(topic=self.topic, user=self.user)

        utils.login(self)
        response = self.client.get(reverse(
            "spirit:user:topics", kwargs={
                'pk': self.user2.pk, 'slug': self.user2.st.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['topics']), [self.topic])
        self.assertEqual(response.context['topics'][0].bookmark, bookmark)

    @override_djconfig(topics_per_page=1)
    def test_profile_topics_paginate(self):
        """
        profile user's topics paginated
        """
        topic = utils.create_topic(self.category, user=self.user2)

        utils.login(self)
        response = self.client.get(reverse(
            "spirit:user:topics",
            kwargs={'pk': self.user2.pk, 'slug': self.user2.st.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['topics']), [topic])

    def test_profile_topics_dont_show_removed_or_private(self):
        """
        dont show private topics or removed
        """
        Topic.objects.all().delete()

        category = utils.create_category()
        category_removed = utils.create_category(is_removed=True)
        subcategory = utils.create_category(parent=category_removed)
        subcategory_removed = utils.create_category(parent=category, is_removed=True)
        utils.create_private_topic(user=self.user2)
        utils.create_topic(category=category, user=self.user2, is_removed=True)
        utils.create_topic(category=category_removed, user=self.user2)
        utils.create_topic(category=subcategory, user=self.user2)
        utils.create_topic(category=subcategory_removed, user=self.user2)

        utils.login(self)
        response = self.client.get(reverse(
            "spirit:user:topics",
            kwargs={'pk': self.user2.pk, 'slug': self.user2.st.slug}))
        self.assertEqual(list(response.context['topics']), [])

    def test_profile_topics_invalid_slug(self):
        """
        profile user's topics
        """
        utils.login(self)
        response = self.client.get(reverse(
            "spirit:user:topics",
            kwargs={'pk': self.user2.pk, 'slug': "invalid"}))
        expected_url = reverse(
            "spirit:user:topics",
            kwargs={'pk': self.user2.pk, 'slug': self.user2.st.slug})
        self.assertRedirects(response, expected_url, status_code=301)

    def test_profile_comments(self):
        """
        profile user's comments
        """
        utils.login(self)
        comment = utils.create_comment(user=self.user2, topic=self.topic)
        utils.create_comment(user=self.user, topic=self.topic)
        response = self.client.get(reverse(
            "spirit:user:detail",
            kwargs={'pk': self.user2.pk, 'slug': self.user2.st.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['comments']), [comment])
        self.assertEqual(response.context['p_user'], self.user2)

    def test_profile_comments_order(self):
        """
        comments ordered by date
        """
        comment_a = utils.create_comment(user=self.user2, topic=self.topic)
        comment_b = utils.create_comment(user=self.user2, topic=self.topic)
        comment_c = utils.create_comment(user=self.user2, topic=self.topic)

        Comment.objects.filter(pk=comment_a.pk).update(
            date=timezone.now() - datetime.timedelta(days=10))
        Comment.objects.filter(pk=comment_c.pk).update(
            date=timezone.now() - datetime.timedelta(days=5))

        utils.login(self)
        response = self.client.get(reverse(
            "spirit:user:detail",
            kwargs={'pk': self.user2.pk, 'slug': self.user2.st.slug}))
        self.assertEqual(
            list(response.context['comments']),
            [comment_b, comment_c, comment_a])

    @override_djconfig(comments_per_page=1)
    def test_profile_comments_paginate(self):
        """
        profile user's comments paginated
        """
        utils.create_comment(user=self.user2, topic=self.topic)
        comment = utils.create_comment(user=self.user2, topic=self.topic)

        utils.login(self)
        response = self.client.get(reverse(
            "spirit:user:detail",
            kwargs={'pk': self.user2.pk, 'slug': self.user2.st.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['comments']), [comment])

    def test_profile_comments_dont_show_removed_or_private(self):
        """
        dont show private topics or removed
        """
        category = utils.create_category()
        category_removed = utils.create_category(is_removed=True)
        subcategory = utils.create_category(parent=category_removed)
        subcategory_removed = utils.create_category(parent=category, is_removed=True)
        topic_a = utils.create_private_topic(user=self.user2)
        topic_b = utils.create_topic(category=category, is_removed=True)
        topic_c = utils.create_topic(category=category_removed)
        topic_d = utils.create_topic(category=subcategory)
        topic_e = utils.create_topic(category=subcategory_removed)
        utils.create_comment(user=self.user2, topic=topic_a.topic)
        utils.create_comment(user=self.user2, topic=topic_b)
        utils.create_comment(user=self.user2, topic=topic_c)
        utils.create_comment(user=self.user2, topic=topic_d)
        utils.create_comment(user=self.user2, topic=topic_e)

        utils.login(self)
        response = self.client.get(reverse(
            "spirit:user:detail",
            kwargs={'pk': self.user2.pk, 'slug': self.user2.st.slug}))
        self.assertEqual(list(response.context['comments']), [])

    def test_profile_comments_invalid_slug(self):
        """
        profile user's comments, invalid user slug
        """
        utils.login(self)
        response = self.client.get(reverse(
            "spirit:user:detail",
            kwargs={'pk': self.user2.pk, 'slug': "invalid"}))
        expected_url = reverse(
            "spirit:user:detail",
            kwargs={'pk': self.user2.pk, 'slug': self.user2.st.slug})
        self.assertRedirects(response, expected_url, status_code=301)

    def test_profile_likes(self):
        """
        profile user's likes
        """
        utils.login(self)
        comment = utils.create_comment(user=self.user, topic=self.topic)
        comment2 = utils.create_comment(user=self.user2, topic=self.topic)
        like = CommentLike.objects.create(user=self.user2, comment=comment)
        CommentLike.objects.create(user=self.user, comment=comment2)
        response = self.client.get(reverse(
            "spirit:user:likes",
            kwargs={'pk': self.user2.pk, 'slug': self.user2.st.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['comments']), [like.comment])
        self.assertEqual(response.context['p_user'], self.user2)

    def test_profile_likes_order(self):
        """
        comments ordered by date
        """
        comment_a = utils.create_comment(user=self.user, topic=self.topic)
        comment_b = utils.create_comment(user=self.user, topic=self.topic)
        comment_c = utils.create_comment(user=self.user, topic=self.topic)
        like_a = CommentLike.objects.create(user=self.user2, comment=comment_a)
        CommentLike.objects.create(user=self.user2, comment=comment_b)
        like_c = CommentLike.objects.create(user=self.user2, comment=comment_c)

        CommentLike.objects.filter(pk=like_a.pk).update(
            date=timezone.now() - datetime.timedelta(days=10))
        CommentLike.objects.filter(pk=like_c.pk).update(
            date=timezone.now() - datetime.timedelta(days=5))

        utils.login(self)
        response = self.client.get(reverse(
            "spirit:user:likes",
            kwargs={'pk': self.user2.pk, 'slug': self.user2.st.slug}))
        self.assertEqual(
            list(response.context['comments']),
            [comment_b, comment_c, comment_a])

    def test_profile_likes_dont_show_removed_or_private(self):
        """
        dont show private topics or removed
        """
        category = utils.create_category()
        category_removed = utils.create_category(is_removed=True)
        subcategory = utils.create_category(parent=category_removed)
        subcategory_removed = utils.create_category(parent=category, is_removed=True)
        topic_a = utils.create_private_topic(user=self.user2)
        topic_b = utils.create_topic(category=category, is_removed=True)
        topic_c = utils.create_topic(category=category_removed)
        topic_d = utils.create_topic(category=subcategory)
        topic_e = utils.create_topic(category=subcategory_removed)
        comment_a = utils.create_comment(user=self.user2, topic=topic_a.topic)
        comment_b = utils.create_comment(user=self.user, topic=topic_b)
        comment_c = utils.create_comment(user=self.user, topic=topic_c)
        comment_d = utils.create_comment(user=self.user, topic=topic_d)
        comment_e = utils.create_comment(user=self.user, topic=topic_e)
        CommentLike.objects.create(user=self.user2, comment=comment_a)
        CommentLike.objects.create(user=self.user2, comment=comment_b)
        CommentLike.objects.create(user=self.user2, comment=comment_c)
        CommentLike.objects.create(user=self.user2, comment=comment_d)
        CommentLike.objects.create(user=self.user2, comment=comment_e)

        utils.login(self)
        response = self.client.get(reverse(
            "spirit:user:likes",
            kwargs={'pk': self.user2.pk, 'slug': self.user2.st.slug}))
        self.assertEqual(list(response.context['comments']), [])

    def test_profile_likes_invalid_slug(self):
        """
        profile user's likes, invalid user slug
        """
        utils.login(self)
        response = self.client.get(reverse(
            "spirit:user:likes",
            kwargs={'pk': self.user2.pk, 'slug': "invalid"}))
        expected_url = reverse(
            "spirit:user:likes",
            kwargs={'pk': self.user2.pk, 'slug': self.user2.st.slug})
        self.assertRedirects(response, expected_url, status_code=301)

    @override_djconfig(comments_per_page=1)
    def test_profile_likes_paginate(self):
        """
        profile user's likes paginate
        """
        comment = utils.create_comment(user=self.user2, topic=self.topic)
        comment2 = utils.create_comment(user=self.user2, topic=self.topic)
        CommentLike.objects.create(user=self.user2, comment=comment)
        like = CommentLike.objects.create(user=self.user2, comment=comment2)

        utils.login(self)
        response = self.client.get(reverse(
            "spirit:user:likes",
            kwargs={'pk': self.user2.pk, 'slug': self.user2.st.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['comments']), [like.comment])

    def test_profile_update(self):
        """
        profile update
        """
        utils.login(self)
        # get
        response = self.client.get(reverse('spirit:user:update'))
        self.assertEqual(response.status_code, 200)
        # post
        form_data = {
            'first_name': 'foo', 'last_name': 'bar',
            'location': 'spirit', 'timezone': self.user.st.timezone,
            'notify_when': self.user.st.Notify.NEVER}
        response = self.client.post(
            reverse('spirit:user:update'), form_data)
        expected_url = reverse('spirit:user:update')
        self.assertRedirects(response, expected_url, status_code=302)

    @utils.with_test_storage
    @utils.immediate_on_commit
    @override_settings(ST_ALLOWED_AVATAR_FORMAT=('gif',))
    def test_profile_update_avatar(self):
        utils.clean_media()
        utils.login(self)
        content = (
            b'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00'
            b'\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')
        form_data = {
            'first_name': 'foo',
            'last_name': 'bar',
            'location': 'spirit',
            'timezone': self.user.st.timezone,
            'notify_when': self.user.st.Notify.NEVER,
            'avatar': SimpleUploadedFile('foo.gif', content=content)}
        response = self.client.post(
            reverse('spirit:user:update'), form_data)
        expected_url = reverse('spirit:user:update')
        self.assertRedirects(response, expected_url, status_code=302)
        self.user.refresh_from_db()
        self.assertTrue(spirit_storage.exists(self.user.st.avatar.name))
        self.assertEqual(
            self.user.st.avatar.name,
            'spirit/avatars/{}/pic_test.jpg'.format(self.user.pk))
        self.assertTrue(spirit_storage.exists(
            'spirit/avatars/{}/pic_test_small_test.jpg'.format(self.user.pk)))

    @utils.with_test_storage
    @utils.immediate_on_commit
    @override_settings(ST_ALLOWED_AVATAR_FORMAT=('gif',))
    def test_profile_update_change_avatar(self):
        utils.clean_media()
        utils.login(self)
        content = (
            b'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00'
            b'\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')
        # store initial avatar
        self.user.st.avatar = SimpleUploadedFile('foo.gif', content=content)
        self.user.st.save()
        self.assertTrue(spirit_storage.exists(self.user.st.avatar.name))
        self.assertEqual(
            self.user.st.avatar.name,
            'spirit/avatars/{}/pic_test.gif'.format(self.user.pk))
        # change avatar
        form_data = {
            'first_name': 'foo',
            'last_name': 'bar',
            'location': 'spirit',
            'timezone': self.user.st.timezone,
            'notify_when': self.user.st.Notify.NEVER,
            'avatar': SimpleUploadedFile('foo.gif', content=content)}
        response = self.client.post(
            reverse('spirit:user:update'), form_data)
        expected_url = reverse('spirit:user:update')
        self.assertRedirects(response, expected_url, status_code=302)
        self.user.refresh_from_db()
        self.assertTrue(spirit_storage.exists(self.user.st.avatar.name))
        self.assertEqual(
            self.user.st.avatar.name,
            'spirit/avatars/{}/pic_test.jpg'.format(self.user.pk))
        with self.user.st.avatar.open() as fh:
            self.assertNotEqual(fh.read(), content)
        self.assertTrue(spirit_storage.exists(
            'spirit/avatars/{}/pic_test_small_test.jpg'.format(self.user.pk)))

    @utils.with_test_storage
    @utils.immediate_on_commit
    @override_settings(ST_ALLOWED_AVATAR_FORMAT=('gif',))
    def test_profile_update_no_change_avatar(self):
        utils.clean_media()
        utils.login(self)
        content = (
            b'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00'
            b'\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')
        # store initial avatar
        self.user.st.avatar = SimpleUploadedFile('foo.gif', content=content)
        self.user.st.save()
        self.assertTrue(spirit_storage.exists(self.user.st.avatar.name))
        self.assertEqual(
            self.user.st.avatar.name,
            'spirit/avatars/{}/pic_test.gif'.format(self.user.pk))
        # do not change avatar
        form_data = {
            'first_name': 'foo',
            'last_name': 'bar',
            'location': 'spirit',
            'timezone': self.user.st.timezone,
            'notify_when': self.user.st.Notify.NEVER}
        response = self.client.post(
            reverse('spirit:user:update'), form_data)
        expected_url = reverse('spirit:user:update')
        self.assertRedirects(response, expected_url, status_code=302)
        self.user.refresh_from_db()
        self.assertTrue(spirit_storage.exists(self.user.st.avatar.name))
        self.assertEqual(
            self.user.st.avatar.name,
            'spirit/avatars/{}/pic_test.gif'.format(self.user.pk))
        with self.user.st.avatar.open() as fh:
            self.assertEqual(fh.read(), content)

    def test_profile_password_change(self):
        """
        profile password change
        """
        user = utils.create_user(password="foo")
        utils.login(self, user=user, password="foo")
        form_data = {
            'old_password': 'foo',
            'new_password1': 'bar',
            'new_password2': 'bar'}
        response = self.client.post(
            reverse('spirit:user:password-change'), form_data)
        expected_url = reverse("spirit:user:update")
        self.assertRedirects(response, expected_url, status_code=302)
        utils.login(self, user=user, password="bar")

        # get
        response = self.client.get(reverse('spirit:user:password-change'))
        self.assertEqual(response.status_code, 200)

    def test_profile_password_change_re_login(self):
        """
        Changing the password should invalidate the session
        """
        user = utils.create_user(password="foo")
        utils.login(self, user=user, password="foo")
        old_hash = self.client.session[HASH_SESSION_KEY]

        form_data = {
            'old_password': 'foo',
            'new_password1': 'bar',
            'new_password2': 'bar'}
        response = self.client.post(reverse('spirit:user:password-change'), form_data)
        expected_url = reverse("spirit:user:update")
        self.assertRedirects(response, expected_url, status_code=302)

        self.assertNotEqual(old_hash, self.client.session[HASH_SESSION_KEY])

    def test_email_change_confirm(self):
        """
        email change confirmation
        """
        utils.login(self)
        new_email = "newfoo@bar.com"
        token = UserEmailChangeTokenGenerator().generate(self.user, new_email)
        response = self.client.get(reverse(
            'spirit:user:email-change-confirm', kwargs={'token': token}))
        expected_url = reverse("spirit:user:update")
        self.assertRedirects(response, expected_url, status_code=302)
        self.assertEqual(User.objects.get(pk=self.user.pk).email, new_email)

    def test_email_change_confirm_invalid(self):
        """
        The token should expire after email change
        """
        utils.login(self)
        old_email = "oldfoo@bar.com"
        token = UserEmailChangeTokenGenerator().generate(self.user, old_email)
        new_email = "newfoo@bar.com"
        User.objects.filter(pk=self.user.pk).update(email=new_email)
        response = self.client.get(reverse(
            'spirit:user:email-change-confirm', kwargs={'token': token}))
        expected_url = reverse("spirit:user:update")
        self.assertRedirects(response, expected_url, status_code=302)
        self.assertEqual(User.objects.get(pk=self.user.pk).email, new_email)

    def test_email_change_duplicated(self):
        """
        email should be unique
        """
        utils.login(self)
        utils.create_user(email="duplicated@bar.com")
        new_email = "duplicated@bar.com"
        old_email = self.user.email
        token = UserEmailChangeTokenGenerator().generate(self.user, new_email)
        self.client.get(reverse(
            'spirit:user:email-change-confirm', kwargs={'token': token}))
        self.assertEqual(User.objects.get(pk=self.user.pk).email, old_email)

    @override_settings(ST_UNIQUE_EMAILS=False)
    def test_email_change_duplicated_allowed(self):
        """
        Duplicated email allowed
        """
        utils.login(self)
        utils.create_user(email="duplicated@bar.com")
        new_email = "duplicated@bar.com"
        token = UserEmailChangeTokenGenerator().generate(self.user, new_email)
        self.client.get(reverse(
            'spirit:user:email-change-confirm', kwargs={'token': token}))
        self.assertEqual(User.objects.get(pk=self.user.pk).email, new_email)

    @utils.immediate_on_commit
    def test_profile_email_change(self):
        """
        email change
        """
        user = utils.create_user(password="foo")
        utils.login(self, user=user, password="foo")
        form_data = {
            'password': 'foo',
            'email': 'newfoo@bar.com'}
        response = self.client.post(
            reverse('spirit:user:email-change'), form_data)
        expected_url = reverse("spirit:user:update")
        self.assertRedirects(response, expected_url, status_code=302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(_("Email change"), mail.outbox[0].subject)

        # get
        response = self.client.get(reverse('spirit:user:email-change'))
        self.assertEqual(response.status_code, 200)

    def test_unsubscribe(self):
        utils.login(self)
        self.user.st.notify = self.user.st.Notify.IMMEDIATELY | self.user.st.Notify.REPLY
        self.user.st.save()
        token = unsub_token(user_id=self.user.pk)
        response = self.client.get(reverse(
            'spirit:user:unsubscribe', kwargs={'pk': self.user.pk, 'token': token}))
        expected_url = reverse("spirit:user:update")
        self.assertRedirects(response, expected_url, status_code=302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.st.notify, self.user.st.Notify.NEVER)

    def test_unsubscribe_bad_user(self):
        utils.login(self)
        self.user.st.notify = self.user.st.Notify.IMMEDIATELY | self.user.st.Notify.REPLY
        self.user.st.save()
        token = unsub_token(user_id=self.user.pk)
        user = utils.create_user()
        response = self.client.get(reverse(
            'spirit:user:unsubscribe', kwargs={'pk': user.pk, 'token': token}))
        expected_url = reverse("spirit:user:update")
        self.assertRedirects(response, expected_url, status_code=302)
        self.user.refresh_from_db()
        self.assertEqual(
            self.user.st.notify,
            self.user.st.Notify.IMMEDIATELY | self.user.st.Notify.REPLY)


class UserFormTest(TestCase):

    def setUp(self):
        utils.cache_clear()
        self.user = utils.create_user()

    def test_profile(self):
        """
        edit user profile
        """
        form_data = {
            'first_name': 'foo', 'last_name': 'bar',
            'location': 'spirit', 'timezone': self.user.st.timezone,
            'notify_when': self.user.st.Notify.NEVER}
        form = UserProfileForm(data=form_data, instance=self.user.st)
        self.assertEqual(form.is_valid(), True)

        form = UserForm(data=form_data, instance=self.user)
        self.assertEqual(form.is_valid(), True)

    def test_profile_timezone_field(self):
        form_data = {
            'first_name': 'foo', 'last_name': 'bar',
            'location': 'spirit', 'timezone': 'UTC',
            'notify_when': self.user.st.Notify.NEVER}

        form = UserProfileForm(data=form_data, instance=self.user.st)
        self.assertEqual(form.is_valid(), True)

        form_data['timezone'] = 'badtimezone'
        form = UserProfileForm(data=form_data, instance=self.user.st)
        self.assertEqual(form.is_valid(), False)
        self.assertTrue('timezone' in form.errors)

    @utils.with_test_storage
    @utils.immediate_on_commit
    @override_settings(ST_ALLOWED_AVATAR_FORMAT=('gif',))
    def test_profile_avatar(self):
        utils.clean_media()
        content = (
            b'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00'
            b'\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')
        form_data = {
            'first_name': 'foo',
            'last_name': 'bar',
            'location': 'spirit',
            'timezone': self.user.st.timezone,
            'notify_when': self.user.st.Notify.NEVER}
        data_files = {
            'avatar': SimpleUploadedFile('foo.gif', content=content)}
        form = UserProfileForm(data=form_data, files=data_files, instance=self.user.st)
        self.assertEqual(form.is_valid(), True)
        form.save()
        self.user.refresh_from_db()
        self.assertTrue(spirit_storage.exists(self.user.st.avatar.name))
        self.assertEqual(
            self.user.st.avatar.name,
            'spirit/avatars/{}/pic_test.jpg'.format(self.user.pk))

    def test_email_change(self):
        """
        email change
        """
        user = utils.create_user(password="foo")
        form_data = {'email': 'newfoo@bar.com', 'password': 'foo'}
        form = EmailChangeForm(data=form_data, user=user)
        self.assertEqual(form.is_valid(), True)

    def test_email_change_invalid(self):
        """
        email change invalid
        """
        user = utils.create_user(password="foo", email="newfoo@bar.com")
        form_data = {'email': 'newfoo@bar.com', 'password': 'bad-password'}
        form = EmailChangeForm(data=form_data, user=user)
        self.assertEqual(form.is_valid(), False)
        self.assertNotIn('email', form.cleaned_data)
        self.assertNotIn('password', form.cleaned_data)

    def test_email_change_email_duplication(self):
        """
        email change, don't allow email duplication
        """
        utils.create_user(email="duplicated@bar.com")
        user = utils.create_user(password="foo")
        form_data = {'email': 'duplicated@bar.com', 'password': 'foo'}
        form = EmailChangeForm(data=form_data, user=user)
        self.assertEqual(form.is_valid(), False)
        self.assertNotIn('email', form.cleaned_data)

    @override_settings(ST_UNIQUE_EMAILS=False)
    def test_email_change_email_duplication_allowed(self):
        """
        Duplicated email allowed
        """
        utils.create_user(email="duplicated@bar.com")
        user = utils.create_user(password="foo")
        form_data = {'email': 'duplicated@bar.com', 'password': 'foo'}
        form = EmailChangeForm(data=form_data, user=user)
        self.assertEqual(form.is_valid(), True)

    @override_settings(ST_CASE_INSENSITIVE_EMAILS=True)
    def test_email_change_email_case_insensitive(self):
        """
        Should lower case the email before validating it
        """
        utils.create_user(email="duplicated@bar.com")
        user = utils.create_user(password="foo")
        form_data = {'email': 'DuPlIcAtEd@bAr.COM', 'password': 'foo'}
        form = EmailChangeForm(data=form_data, user=user)
        self.assertEqual(form.is_valid(), False)

    @override_settings(ST_CASE_INSENSITIVE_EMAILS=False)
    def test_email_change_email_case_sensitive(self):
        """
        Should not lower case the email before validating it
        """
        utils.create_user(email="duplicated@bar.com")
        user = utils.create_user(password="foo")
        form_data = {'email': 'DuPlIcAtEd@bAr.COM', 'password': 'foo'}
        form = EmailChangeForm(data=form_data, user=user)
        self.assertEqual(form.is_valid(), True)

    def test_email_check(self):
        """
        Check it's an email
        """
        # Unique email
        form_data = {'email': 'unique@bar.com'}
        form = EmailCheckForm(form_data)
        self.assertTrue(form.is_valid())

        # Duplicated email
        utils.create_user(email="duplicated@bar.com")
        form_data['email'] = "duplicated@bar.com"
        form = EmailCheckForm(form_data)
        self.assertFalse(form.is_valid())

    @override_settings(ST_UNIQUE_EMAILS=False)
    def test_email_check_non_unique(self):
        """
        Duplicated email allowed
        """
        utils.create_user(email="duplicated@bar.com")
        form_data = {'email': 'duplicated@bar.com', }
        form = EmailCheckForm(form_data)
        self.assertTrue(form.is_valid())

    @override_settings(ST_CASE_INSENSITIVE_EMAILS=True)
    def test_email_check_case_insensitive(self):
        """
        Should lower case the email before validating it
        """
        utils.create_user(email="duplicated@bar.com")
        form_data = {'email': 'DuPlIcAtEd@bAr.COM', }
        form = EmailCheckForm(form_data)
        self.assertFalse(form.is_valid())

    @override_settings(ST_CASE_INSENSITIVE_EMAILS=False)
    def test_email_check_case_sensitive(self):
        """
        Should not lower case the email before validating it
        """
        utils.create_user(email="duplicated@bar.com")
        form_data = {'email': 'DuPlIcAtEd@bAr.COM', }
        form = EmailCheckForm(form_data)
        self.assertTrue(form.is_valid())

    def test_notify_when(self):
        form_data = {
            'first_name': 'foo', 'last_name': 'bar',
            'location': 'spirit', 'timezone': self.user.st.timezone,
            'notify_when': self.user.st.Notify.NEVER}
        form = UserProfileForm(data=form_data, instance=self.user.st)
        self.assertEqual(form.is_valid(), True)
        form.save()
        self.user.refresh_from_db()
        self.assertEqual(
            self.user.st.notify_when, self.user.st.Notify.NEVER)

        form_data['notify_when'] = self.user.st.Notify.IMMEDIATELY
        form = UserProfileForm(data=form_data, instance=self.user.st)
        self.assertEqual(
            form.fields['notify_when'].initial, self.user.st.Notify.NEVER)
        self.assertEqual(form.is_valid(), True)
        form.save()
        self.user.refresh_from_db()
        self.assertEqual(
            self.user.st.notify_when, self.user.st.Notify.IMMEDIATELY)

        form_data['notify_when'] = self.user.st.Notify.WEEKLY
        form = UserProfileForm(data=form_data, instance=self.user.st)
        self.assertEqual(
            form.fields['notify_when'].initial, self.user.st.Notify.IMMEDIATELY)
        self.assertEqual(form.is_valid(), True)
        form.save()
        self.user.refresh_from_db()
        self.assertEqual(
            self.user.st.notify_when, self.user.st.Notify.WEEKLY)

        form = UserProfileForm(data=form_data, instance=self.user.st)
        self.assertEqual(
            form.fields['notify_when'].initial, self.user.st.Notify.WEEKLY)
        self.assertEqual(form.is_valid(), True)

    def test_notify(self):
        form_data = {
            'first_name': 'foo', 'last_name': 'bar',
            'location': 'spirit', 'timezone': self.user.st.timezone,
            'notify_when': self.user.st.Notify.IMMEDIATELY}
        form = UserProfileForm(data=form_data, instance=self.user.st)
        self.assertEqual(form.is_valid(), True)
        form.save()
        self.user.refresh_from_db()
        self.assertEqual(
            self.user.st.notify_when, self.user.st.Notify.IMMEDIATELY)
        self.assertFalse(
            self.user.st.notify & self.user.st.Notify.MENTION)
        self.assertFalse(
            self.user.st.notify & self.user.st.Notify.REPLY)

        form_data['notify_when'] = self.user.st.Notify.WEEKLY
        form_data['notify_mentions'] = True
        form = UserProfileForm(data=form_data, instance=self.user.st)
        self.assertFalse(form.fields['notify_mentions'].initial)
        self.assertFalse(form.fields['notify_replies'].initial)
        self.assertEqual(form.is_valid(), True)
        form.save()
        self.user.refresh_from_db()
        self.assertEqual(
            self.user.st.notify_when, self.user.st.Notify.WEEKLY)
        self.assertTrue(
            self.user.st.notify & self.user.st.Notify.MENTION)
        self.assertFalse(
            self.user.st.notify & self.user.st.Notify.REPLY)

        form_data['notify_when'] = self.user.st.Notify.IMMEDIATELY
        form_data['notify_mentions'] = False
        form_data['notify_replies'] = True
        form = UserProfileForm(data=form_data, instance=self.user.st)
        self.assertEqual(
            form.fields['notify_when'].initial, self.user.st.Notify.WEEKLY)
        self.assertTrue(form.fields['notify_mentions'].initial)
        self.assertFalse(form.fields['notify_replies'].initial)
        self.assertEqual(form.is_valid(), True)
        form.save()
        self.user.refresh_from_db()
        self.assertEqual(
            self.user.st.notify_when, self.user.st.Notify.IMMEDIATELY)
        self.assertFalse(
            self.user.st.notify & self.user.st.Notify.MENTION)
        self.assertTrue(
            self.user.st.notify & self.user.st.Notify.REPLY)

        form_data['notify_mentions'] = True
        form_data['notify_replies'] = True
        form = UserProfileForm(data=form_data, instance=self.user.st)
        self.assertEqual(
            form.fields['notify_when'].initial, self.user.st.Notify.IMMEDIATELY)
        self.assertFalse(form.fields['notify_mentions'].initial)
        self.assertTrue(form.fields['notify_replies'].initial)
        self.assertEqual(form.is_valid(), True)
        form.save()
        self.user.refresh_from_db()
        self.assertEqual(
            self.user.st.notify_when, self.user.st.Notify.IMMEDIATELY)
        self.assertTrue(
            self.user.st.notify & self.user.st.Notify.MENTION)
        self.assertTrue(
            self.user.st.notify & self.user.st.Notify.REPLY)

        form = UserProfileForm(data=form_data, instance=self.user.st)
        self.assertTrue(form.fields['notify_mentions'].initial)
        self.assertTrue(form.fields['notify_replies'].initial)
        self.assertEqual(form.is_valid(), True)


class UserModelTest(TestCase):

    def setUp(self):
        utils.cache_clear()

    def test_user_superuser(self):
        """
        is_superuser should always be is_administrator and is_moderator
        test model
        """
        user = User(is_superuser=True)
        user.save()
        self.assertTrue(user.st.is_administrator)
        self.assertTrue(user.st.is_moderator)

    def test_user_administrator(self):
        """
        is_administrator should always be is_moderator
        """
        user = User()
        user.save()
        user.st.is_administrator = True
        user.st.save()
        self.assertTrue(user.st.is_moderator)

    @override_settings(ST_DOUBLE_POST_THRESHOLD_MINUTES=1)
    def test_update_post_hash(self):
        """
        Should update the last post hash and date
            if stored hash doesn't matches the new one
            and/or stored date is higher than the threshold
        """
        user = User()
        user.save()
        self.assertTrue(user.st.update_post_hash('my_hash'))
        self.assertFalse(user.st.update_post_hash('my_hash'))
        self.assertTrue(user.st.update_post_hash('my_new_hash'))
        self.assertFalse(user.st.update_post_hash('my_new_hash'))

    @override_settings(ST_DOUBLE_POST_THRESHOLD_MINUTES=10)
    def test_update_post_hash_threshold(self):
        """
        Should update the last post hash when the time threshold has past
        """
        user = User()
        user.save()
        self.assertTrue(user.st.update_post_hash('my_hash'))
        self.assertFalse(user.st.update_post_hash('my_hash'))
        user.st.last_post_on = timezone.now() - datetime.timedelta(minutes=11)
        user.st.save()
        self.assertTrue(user.st.update_post_hash('my_hash'))
        self.assertFalse(user.st.update_post_hash('my_hash'))

    @override_settings(ST_DOUBLE_POST_THRESHOLD_MINUTES=1)
    def test_update_post_hash_threshold(self):
        """
        Should update the last post hash and date for the current user
        """
        user = User(username='foo')
        user.save()
        user_b = User(username='bar')
        user_b.save()
        self.assertEqual('', User.objects.get(pk=user.pk).st.last_post_hash)
        self.assertEqual('', User.objects.get(pk=user_b.pk).st.last_post_hash)
        self.assertTrue(user.st.update_post_hash('my_hash'))
        self.assertEqual('my_hash', User.objects.get(pk=user.pk).st.last_post_hash)
        self.assertEqual('', User.objects.get(pk=user_b.pk).st.last_post_hash)

    @utils.with_test_storage
    def test_small_avatar_name(self):
        user = User(username='foo')
        user.save()
        content = (
            b'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00'
            b'\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')
        user.st.avatar = SimpleUploadedFile('foo.gif', content=content)
        user.st.save()
        self.assertEqual(
            user.st.small_avatar_name(),
            'spirit/avatars/{}/pic_test_small.gif'.format(user.pk))

    @utils.with_test_storage
    def test_small_avatar_url(self):
        user = User(username='foo')
        user.save()
        content = (
            b'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00'
            b'\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')
        user.st.avatar = SimpleUploadedFile('foo.gif', content=content)
        user.st.save()
        self.assertEqual(
            user.st.small_avatar_url(),
            '/media/spirit/avatars/{}/pic_test_small.gif'.format(user.pk))


class SignalsUserTests(TestCase):

    def setUp(self):
        utils.cache_clear()

    def test_profile_creation_on_save(self):
        """Should create a profile on user save"""
        user = utils.create_user()
        self.assertTrue(UserProfile.objects.filter(user=user).exists())
        self.assertEqual(user.st, UserProfile.objects.get(user=user))

    @override_settings(ST_CASE_INSENSITIVE_USERNAMES=True)
    def test_profile_creation_on_user_create_case_insensitive(self):
        user = utils.create_user(username='UnIqUeFoO')
        self.assertTrue(user.username, 'uniquefoo')
        self.assertTrue(
            User.objects.filter(username='uniquefoo').exists())
        self.assertTrue(
            UserProfile.objects.filter(
                nickname='UnIqUeFoO',
                user_id=user.pk
            ).exists())

    @override_settings(ST_CASE_INSENSITIVE_USERNAMES=False)
    def test_profile_creation_on_user_create_case_insensitive_off(self):
        user = utils.create_user(username='UnIqUeFoO')
        self.assertTrue(user.username, 'UnIqUeFoO')
        self.assertTrue(
            User.objects.filter(username='UnIqUeFoO').exists())
        self.assertTrue(
            UserProfile.objects.filter(
                nickname='UnIqUeFoO',
                user_id=user.pk
            ).exists())

    def test_profile_notify(self):
        user = utils.create_user()
        self.assertEqual(
            user.st.notify,
            user.st.Notify.NEVER |
            user.st.Notify.MENTION |
            user.st.Notify.REPLY)
        with override_settings(ST_NOTIFY_WHEN='immediately'):
            user = utils.create_user()
            self.assertEqual(
                user.st.notify,
                user.st.Notify.IMMEDIATELY |
                user.st.Notify.MENTION |
                user.st.Notify.REPLY)
        with override_settings(ST_NOTIFY_WHEN='weekly'):
            user = utils.create_user()
            self.assertEqual(
                user.st.notify,
                user.st.Notify.WEEKLY |
                user.st.Notify.MENTION |
                user.st.Notify.REPLY)
        with override_settings(ST_NOTIFY_WHEN='never'):
            user = utils.create_user()
            self.assertEqual(
                user.st.notify,
                user.st.Notify.NEVER |
                user.st.Notify.MENTION |
                user.st.Notify.REPLY)


class UtilsUserTests(TransactionTestCase):

    def setUp(self):
        utils.cache_clear()
        self.user = utils.create_user()

    def test_user_activation_token_generator(self):
        """
        Validate if user can be activated
        """
        self.user.st.is_verified = False

        activation_token = UserActivationTokenGenerator()
        token = activation_token.generate(self.user)
        self.assertTrue(activation_token.is_valid(self.user, token))
        self.assertFalse(activation_token.is_valid(self.user, "bad token"))

        # Invalid after verification
        self.user.st.is_verified = True
        self.assertFalse(activation_token.is_valid(self.user, token))

        # Invalid for different user
        user2 = utils.create_user()
        self.assertFalse(activation_token.is_valid(user2, token))

    def test_user_email_change_token_generator(self):
        """
        Email change
        """
        new_email = "footoken@bar.com"
        email_change_token = UserEmailChangeTokenGenerator()
        token = email_change_token.generate(self.user, new_email)
        self.assertTrue(email_change_token.is_valid(self.user, token))
        self.assertFalse(email_change_token.is_valid(self.user, "bad token"))

        # get new email
        self.assertTrue(email_change_token.is_valid(self.user, token))
        self.assertEqual(email_change_token.get_email(), new_email)

        # Invalid for different user
        user2 = utils.create_user()
        self.assertFalse(email_change_token.is_valid(user2, token))

        # Invalid after email change
        self.user.email = "email_changed@bar.com"
        self.assertFalse(email_change_token.is_valid(self.user, token))

    @override_settings(
        ST_TASK_MANAGER='test', DEFAULT_FROM_EMAIL='test@test.com')
    @utils.immediate_on_commit
    def test_user_activation_email(self):
        """
        Send activation email
        """
        req = RequestFactory().get('/')

        send_activation_email(req, self.user)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, _("User activation"))
        self.assertEqual(mail.outbox[0].from_email, 'test@test.com')
        self.assertIn('https://example.com/user/', mail.outbox[0].body)
        self.assertEqual(mail.outbox[0].to, [self.user.email])

    @override_settings(
        ST_TASK_MANAGER='test', DEFAULT_FROM_EMAIL='test@test.com')
    def test_email_change_email(self):
        """
        Send change email
        """
        req = RequestFactory().get('/')
        new_email = "newfoobar@bar.com"

        send_email_change_email(req, self.user, new_email)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, _("Email change"))
        self.assertEqual(mail.outbox[0].from_email, 'test@test.com')
        self.assertIn('https://example.com/user/', mail.outbox[0].body)
        self.assertEqual(mail.outbox[0].to, [self.user.email])


class TimezoneMiddlewareTest(TestCase):

    def setUp(self):
        timezone.deactivate()
        utils.cache_clear()
        self.user = utils.create_user()

    @override_settings(TIME_ZONE='UTC')
    def test_timezone(self):
        """
        Should activate the user timezone
        """
        timezone.deactivate()
        utils.login(self)
        req = RequestFactory().get('/')
        req.user = self.user
        time_zone = 'America/Argentina/Buenos_Aires'
        self.user.st.timezone = time_zone

        self.assertEqual(timezone.get_current_timezone().zone, 'UTC')
        middleware.TimezoneMiddleware(
            lambda req: HttpResponse(status=500)).process_request(req)
        self.assertEqual(timezone.get_current_timezone().zone, time_zone)

    @override_settings(TIME_ZONE='UTC')
    def test_timezone_bad_tz(self):
        timezone.deactivate()
        utils.login(self)
        req = RequestFactory().get('/')
        req.user = self.user
        self.user.st.timezone = 'badtimezone'

        time_zone = 'America/Argentina/Buenos_Aires'
        timezone.activate(time_zone)
        self.assertEqual(timezone.get_current_timezone().zone, time_zone)
        middleware.TimezoneMiddleware(
            lambda req: HttpResponse(status=500)).process_request(req)
        self.assertEqual(timezone.get_current_timezone().zone, 'UTC')

    @override_settings(TIME_ZONE='UTC')
    def test_timezone_anonymous_user(self):
        class AnonymUserMock(object):
            @property
            def is_authenticated(self):
                return False

        timezone.deactivate()
        req = RequestFactory().get('/')
        req.user = AnonymUserMock()

        time_zone = 'America/Argentina/Buenos_Aires'
        timezone.activate(time_zone)
        self.assertEqual(timezone.get_current_timezone().zone, time_zone)
        middleware.TimezoneMiddleware(
            lambda req: HttpResponse(status=500)).process_request(req)
        self.assertEqual(timezone.get_current_timezone().zone, 'UTC')


class LastIPMiddlewareTest(TestCase):

    def setUp(self):
        utils.cache_clear()
        self.user = utils.create_user()

    def test_last_ip(self):
        """
        Should update user last_ip
        """
        req = RequestFactory().get('/')
        req.user = self.user
        self.assertIsNone(User.objects.get(pk=self.user.pk).st.last_ip)
        req.META['REMOTE_ADDR'] = '123.123.123.123'
        self.assertIsNone(
            middleware.LastIPMiddleware(lambda req: HttpResponse(status=500))
            .process_request(req))
        self.assertEqual(
            User.objects.get(pk=self.user.pk).st.last_ip,
            '123.123.123.123')
        req.META['REMOTE_ADDR'] = '321.321.321.321'
        self.assertIsNone(
            middleware.LastIPMiddleware(lambda req: HttpResponse(status=500))
            .process_request(req))
        self.assertEqual(
            User.objects.get(pk=self.user.pk).st.last_ip,
            '321.321.321.321')

    def test_last_ip_no_update(self):
        """
        Should update user last_ip
        """
        req = RequestFactory().get('/')
        req.user = self.user
        self.user.st.last_ip = '123.123.123.123'
        self.user.st.save()
        self.assertEqual(
            User.objects.get(pk=self.user.pk).st.last_ip,
            '123.123.123.123')
        req.META['REMOTE_ADDR'] = '123.123.123.123'
        self.assertIsNone(
            middleware.LastIPMiddleware(lambda req: HttpResponse(status=500))
            .process_request(req))
        self.assertEqual(
            User.objects.get(pk=self.user.pk).st.last_ip,
            '123.123.123.123')

    def test_last_ip_update(self):
        """
        Should update user last_ip
        """
        req = RequestFactory().get('/')
        req.user = self.user
        self.user.st.last_ip = '123.123.123.123'
        self.user.st.save()
        self.assertEqual(
            User.objects.get(pk=self.user.pk).st.last_ip,
            '123.123.123.123')
        req.META['REMOTE_ADDR'] = '321.321.321.321'
        self.assertIsNone(
            middleware.LastIPMiddleware(lambda req: HttpResponse(status=500))
            .process_request(req))
        self.assertEqual(
            User.objects.get(pk=self.user.pk).st.last_ip,
            '321.321.321.321')

    def test_last_ip_anonym_user(self):
        """
        Should do nothing
        """
        req = RequestFactory().get('/')
        req.user = AnonymousUser()
        self.assertIsNone(
            middleware.LastIPMiddleware(lambda req: HttpResponse(status=500))
            .process_request(req))

    def test_on_client(self):
        """
        Should be called on a request
        """
        utils.login(self)
        self.assertIsNone(User.objects.get(pk=self.user.pk).st.last_ip)
        response = self.client.get(
            reverse('spirit:index'), REMOTE_ADDR='123.123.123.123')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            User.objects.get(pk=self.user.pk).st.last_ip,
            '123.123.123.123')


class LastSeenMiddlewareTest(TestCase):

    def setUp(self):
        utils.cache_clear()
        self.user = utils.create_user()

    @override_settings(ST_USER_LAST_SEEN_THRESHOLD_MINUTES=1)
    def test_last_seen(self):
        """
        Should update user last_seen when threshold is reached
        """
        req = RequestFactory().get('/')
        req.user = self.user
        self.assertTrue(req.user.is_authenticated)
        delta = datetime.timedelta(
            seconds=settings.ST_USER_LAST_SEEN_THRESHOLD_MINUTES * 60 + 1)
        self.assertEqual(
            UserProfile.objects
                .filter(pk=req.user.st.pk)
                .update(last_seen=timezone.now() - delta), 1)
        # Some DBs don't save microseconds, so get the real value
        last_seen = UserProfile.objects.get(pk=req.user.st.pk).last_seen
        req.user.st.last_seen = last_seen
        self.assertIsNone(
            middleware.LastSeenMiddleware(lambda req: HttpResponse(status=500))
            .process_request(req))
        self.assertGreater(
            UserProfile.objects.get(pk=req.user.st.pk).last_seen,
            last_seen)

    @override_settings(ST_USER_LAST_SEEN_THRESHOLD_MINUTES=1)
    def test_last_seen_no_update(self):
        """
        Should not update user last_seen when threshold is not reached
        """
        req = RequestFactory().get('/')
        req.user = self.user
        self.assertTrue(req.user.is_authenticated)
        delta = datetime.timedelta(
            seconds=settings.ST_USER_LAST_SEEN_THRESHOLD_MINUTES * 60 - 1)
        self.assertEqual(
            UserProfile.objects
                .filter(pk=req.user.st.pk)
                .update(last_seen=timezone.now() - delta), 1)
        last_seen = UserProfile.objects.get(pk=req.user.st.pk).last_seen
        req.user.st.last_seen = last_seen
        self.assertIsNone(
            middleware.LastSeenMiddleware(lambda req: HttpResponse(status=500))
            .process_request(req))
        self.assertEqual(
            UserProfile.objects.get(pk=req.user.st.pk).last_seen,
            last_seen)

    def test_last_seen_anonym_user(self):
        """
        Should do nothing
        """
        req = RequestFactory().get('/')
        req.user = AnonymousUser()
        self.assertFalse(req.user.is_authenticated)
        self.assertIsNone(
            middleware.LastSeenMiddleware(lambda req: HttpResponse(status=500))
            .process_request(req))

    @override_settings(ST_USER_LAST_SEEN_THRESHOLD_MINUTES=1)
    def test_on_client(self):
        """
        Should be called on a request
        """
        utils.login(self)
        delta = datetime.timedelta(
            seconds=settings.ST_USER_LAST_SEEN_THRESHOLD_MINUTES * 60 + 1)
        self.assertEqual(
            UserProfile.objects
                .filter(pk=self.user.st.pk)
                .update(last_seen=timezone.now() - delta), 1)
        last_seen = UserProfile.objects.get(pk=self.user.st.pk).last_seen
        response = self.client.get(reverse('spirit:index'))
        self.assertEqual(response.status_code, 200)
        self.assertGreater(
            UserProfile.objects.get(pk=self.user.st.pk).last_seen,
            last_seen)


class ActiveUserMiddlewareTest(TestCase):

    def setUp(self):
        utils.cache_clear()
        self.user = utils.create_user()

    def test_active_user(self):
        """
        Should logout inactive user
        """
        utils.login(self)
        response = self.client.get(reverse('spirit:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.client.session.items())
        User.objects.filter(pk=self.user.pk).update(is_active=False)
        self.user.is_active = False
        response = self.client.get(reverse('spirit:index'))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.client.session.items())

    def test_active_user_mocked(self):
        """
        Should logout inactive user
        """
        client = self.client
        assertTrue = self.assertTrue
        assertFalse = self.assertFalse

        class ActiveUserMiddlewareMock(middleware.ActiveUserMiddleware):
            _calls = []
            def process_request(self, request):
                self._calls.append(request)
                assertTrue(client.session.items())
                ret = super(ActiveUserMiddlewareMock, self).process_request(request)
                assertFalse(client.session.items())
                return ret

        utils.login(self)
        User.objects.filter(pk=self.user.pk).update(is_active=False)
        self.user.is_active = False
        self.assertFalse(ActiveUserMiddlewareMock._calls)

        org_mid, middleware.ActiveUserMiddleware = (
            middleware.ActiveUserMiddleware, ActiveUserMiddlewareMock)
        try:
            self.client.get(reverse('spirit:index'))
        finally:
            middleware.ActiveUserMiddleware = org_mid

        self.assertTrue(ActiveUserMiddlewareMock._calls)

    def test_active_user_is_active(self):
        """
        Should do nothing
        """
        req = RequestFactory().get('/')
        req.user = self.user
        self.assertTrue(req.user.is_authenticated)
        self.assertIsNone(
            middleware.ActiveUserMiddleware(lambda req: HttpResponse(status=500))
            .process_request(req))

    def test_active_user_anonym_user(self):
        """
        Should do nothing
        """
        req = RequestFactory().get('/')
        req.user = AnonymousUser()
        self.assertFalse(req.user.is_authenticated)
        self.assertIsNone(
            middleware.ActiveUserMiddleware(lambda req: HttpResponse(status=500))
            .process_request(req))


class UserMigrationsTest(TestCase):

    def setUp(self):
        utils.cache_clear()

    def test_migration_11(self):
        # create users with the CI feature off
        # to replicate pre feature database state
        with override_settings(ST_CASE_INSENSITIVE_USERNAMES=False):
            utils.create_user(username='FOO')
            utils.create_user(username='BaR')
            utils.create_user(username='baz')
        # default all nicknames to empty
        self.assertEqual(
            UserProfile.objects.all().update(nickname=''), 3)
        data_migration_11.populate_nickname(apps, None)
        self.assertEqual(
            [u.nickname for u in UserProfile.objects.all()],
            ['FOO', 'BaR', 'baz'])

        self.assertEqual(
            [u.username for u in User.objects.all()],
            ['FOO', 'BaR', 'baz'])
        data_migration_11.make_usernames_lower(apps, None)
        self.assertEqual(
            [u.username for u in User.objects.all()],
            ['foo', 'bar', 'baz'])
        self.assertEqual(
            [u.nickname for u in UserProfile.objects.all()],
            ['FOO', 'BaR', 'baz'])

    @override_settings(ST_CASE_INSENSITIVE_USERNAMES=False)
    def test_migration_11_no_ci_usernames(self):
        utils.create_user(username='FOO')
        utils.create_user(username='foo')
        utils.create_user(username='BaR')
        utils.create_user(username='bar')
        utils.create_user(username='baz')

        self.assertEqual(
            UserProfile.objects.all().update(nickname=''), 5)
        data_migration_11.populate_nickname(apps, None)
        self.assertEqual(
            [u.nickname for u in UserProfile.objects.all()],
            ['FOO', 'foo', 'BaR', 'bar', 'baz'])

        self.assertEqual(
            [u.username for u in User.objects.all()],
            ['FOO', 'foo', 'BaR', 'bar', 'baz'])
        data_migration_11.make_usernames_lower(apps, None)
        self.assertEqual(
            [u.username for u in User.objects.all()],
            ['FOO', 'foo', 'BaR', 'bar', 'baz'])
        self.assertEqual(
            [u.nickname for u in UserProfile.objects.all()],
            ['FOO', 'foo', 'BaR', 'bar', 'baz'])

    def test_migration_11_make_usernames_lower_integrity_err(self):
        with override_settings(ST_CASE_INSENSITIVE_USERNAMES=False):
            utils.create_user(username='FOO')
            utils.create_user(username='fOo')
            utils.create_user(username='Foo')
            utils.create_user(username='bar')
            utils.create_user(username='bAr')
            utils.create_user(username='baz')

        self.assertEqual(
            [u.username for u in User.objects.all()],
            ['FOO', 'fOo', 'Foo', 'bar', 'bAr', 'baz'])

        # transaction is already handled
        with self.assertRaises(IntegrityError) as cm:
            data_migration_11.make_usernames_lower(apps, None)
            self.maxDiff = None
            self.assertEqual(
                str(cm.exception),
                "There are two or more users with similar name but "
                "different casing, for example: someUser and SomeUser, "
                "either remove one of them or set the "
                "`ST_CASE_INSENSITIVE_USERNAMES` setting to False. "
                "Then run the upgrade/migration again. Any change was reverted. "
                "Duplicate users are ['FOO', 'fOo', 'Foo', 'bar', 'bAr']")

    def test_migration_11_idempotency(self):
        """Should be idempotent"""
        with override_settings(ST_CASE_INSENSITIVE_USERNAMES=False):
            utils.create_user(username='FOO')
        self.assertEqual(
            UserProfile.objects.all().update(nickname=''), 1)
        data_migration_11.populate_nickname(apps, None)
        data_migration_11.make_usernames_lower(apps, None)
        self.assertEqual(
            [u.username for u in User.objects.all()],
            ['foo'])
        self.assertEqual(
            [u.nickname for u in UserProfile.objects.all()],
            ['FOO'])
        data_migration_11.populate_nickname(apps, None)
        data_migration_11.make_usernames_lower(apps, None)
        self.assertEqual(
            [u.username for u in User.objects.all()],
            ['foo'])
        self.assertEqual(
            [u.nickname for u in UserProfile.objects.all()],
            ['FOO'])

    def test_migration_profiles(self):
        """Should create profile for existing users"""
        foo = utils.create_user(username='foo')
        bar = utils.create_user(username='bar')
        UserProfile.objects.filter(user=foo).delete()
        UserProfile.objects.filter(user=bar).delete()
        foo = User.objects.get(pk=foo.pk)
        bar = User.objects.get(pk=bar.pk)
        with self.assertRaises(ObjectDoesNotExist):
            self.assertIsNone(foo.st)
        with self.assertRaises(ObjectDoesNotExist):
            self.assertIsNone(bar.st)
        data_migration_profiles.migrate_profiles(apps, None)
        self.assertTrue(User.objects.get(pk=foo.pk).st.is_verified)
        self.assertTrue(User.objects.get(pk=bar.pk).st.is_verified)
