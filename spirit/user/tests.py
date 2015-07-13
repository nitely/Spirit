# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import datetime

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.contrib.auth import get_user_model, HASH_SESSION_KEY
from django.core import mail
from django.utils.translation import ugettext as _
from django.utils import timezone
from django.test.utils import override_settings
from django.core.urlresolvers import NoReverseMatch

from djconfig.utils import override_djconfig

from ..core.tests import utils
from .forms import UserProfileForm, EmailChangeForm, UserForm, EmailCheckForm
from .auth.forms import RegistrationForm, ResendActivationForm
from .auth.backends import EmailAuthBackend
from ..comment.like.models import CommentLike
from .utils.tokens import UserActivationTokenGenerator, UserEmailChangeTokenGenerator
from .models import UserProfile
from ..topic.models import Topic
from ..comment.models import Comment
from ..comment.bookmark.models import CommentBookmark

User = get_user_model()


class UserViewTest(TestCase):

    def setUp(self):
        cache.clear()
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

        response = self.client.get(reverse('spirit:user:topics', kwargs={'pk': pk, 'slug': slug}))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('spirit:user:detail', kwargs={'pk': pk, 'slug': slug}))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('spirit:user:likes', kwargs={'pk': pk, 'slug': slug}))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('spirit:user:update'))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('spirit:user:password-change'))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('spirit:user:email-change'))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('spirit:user:email-change-confirm', kwargs={'token': "foo"}))
        self.assertEqual(response.status_code, 302)

    def test_login_email(self):
        """
        try to login by email
        """
        # get
        response = self.client.get(reverse('spirit:user:auth:login'))
        self.assertEqual(response.status_code, 200)

        # post
        form_data = {'username': self.user.email, 'password': "bar"}
        response = self.client.post(reverse('spirit:user:auth:login'),
                                    form_data)
        expected_url = reverse('spirit:user:update')
        self.assertRedirects(response, expected_url, status_code=302)

    def test_login_redirect(self):
        """
        try to login with a logged in user
        """
        utils.login(self)
        response = self.client.get(reverse('spirit:user:auth:login'))
        expected_url = self.user.st.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302)
        # next
        response = self.client.get(reverse('spirit:user:auth:login') + '?next=/fakepath/')
        self.assertRedirects(response, '/fakepath/', status_code=302, target_status_code=404)

    def test_register(self):
        """
        register
        """
        # get
        response = self.client.get(reverse('spirit:user:auth:register'))
        self.assertEqual(response.status_code, 200)

        # post
        form_data = {'username': 'uniquefoo', 'email': 'some@some.com', 'password1': 'pass', 'password2': 'pass'}
        response = self.client.post(reverse('spirit:user:auth:register'),
                                    form_data)
        expected_url = reverse('spirit:user:auth:login')
        self.assertRedirects(response, expected_url, status_code=302)

        # redirect logged in user
        utils.login(self)
        response = self.client.get(reverse('spirit:user:auth:register'))
        self.assertRedirects(response, reverse('spirit:user:update'), status_code=302)

    def test_register_email_sent(self):
        """
        register and send activation email
        """
        form_data = {'username': 'uniquefoo', 'email': 'some@some.com', 'password1': 'pass', 'password2': 'pass'}
        response = self.client.post(reverse('spirit:user:auth:register'), form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].subject, _("User activation"))

    def test_register_next_logged_in(self):
        """
        redirect next on register
        """
        # redirect logged in user
        utils.login(self)
        response = self.client.get(reverse('spirit:user:auth:register') + "?next=/fakepath/")
        self.assertRedirects(response, '/fakepath/', status_code=302, target_status_code=404)

    def test_profile_topics(self):
        """
        profile user's topics
        """
        utils.login(self)
        response = self.client.get(reverse("spirit:user:topics", kwargs={'pk': self.user2.pk,
                                                                            'slug': self.user2.st.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['topics']), [self.topic, ])
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

        Topic.objects.filter(pk=topic_a.pk).update(date=timezone.now() - datetime.timedelta(days=10))
        Topic.objects.filter(pk=topic_c.pk).update(date=timezone.now() - datetime.timedelta(days=5))

        utils.login(self)
        response = self.client.get(reverse("spirit:user:topics", kwargs={'pk': self.user2.pk,
                                                                            'slug': self.user2.st.slug}))
        self.assertEqual(list(response.context['topics']), [topic_b, topic_c, topic_a])

    def test_profile_topics_bookmarks(self):
        """
        profile user's topics with bookmarks
        """
        bookmark = CommentBookmark.objects.create(topic=self.topic, user=self.user)

        utils.login(self)
        response = self.client.get(reverse("spirit:user:topics",
                                           kwargs={'pk': self.user2.pk, 'slug': self.user2.st.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['topics']), [self.topic, ])
        self.assertEqual(response.context['topics'][0].bookmark, bookmark)

    @override_djconfig(topics_per_page=1)
    def test_profile_topics_paginate(self):
        """
        profile user's topics paginated
        """
        topic = utils.create_topic(self.category, user=self.user2)

        utils.login(self)
        response = self.client.get(reverse("spirit:user:topics", kwargs={'pk': self.user2.pk,
                                                                            'slug': self.user2.st.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['topics']), [topic, ])

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
        response = self.client.get(reverse("spirit:user:topics", kwargs={'pk': self.user2.pk,
                                                                            'slug': self.user2.st.slug}))
        self.assertEqual(list(response.context['topics']), [])

    def test_profile_topics_invalid_slug(self):
        """
        profile user's topics
        """
        utils.login(self)
        response = self.client.get(reverse("spirit:user:topics", kwargs={'pk': self.user2.pk,
                                                                            'slug': "invalid"}))
        expected_url = reverse("spirit:user:topics", kwargs={'pk': self.user2.pk,
                                                                'slug': self.user2.st.slug})
        self.assertRedirects(response, expected_url, status_code=301)

    def test_profile_comments(self):
        """
        profile user's comments
        """
        utils.login(self)
        comment = utils.create_comment(user=self.user2, topic=self.topic)
        utils.create_comment(user=self.user, topic=self.topic)
        response = self.client.get(reverse("spirit:user:detail", kwargs={'pk': self.user2.pk,
                                                                            'slug': self.user2.st.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['comments']), [comment, ])
        self.assertEqual(response.context['p_user'], self.user2)

    def test_profile_comments_order(self):
        """
        comments ordered by date
        """
        comment_a = utils.create_comment(user=self.user2, topic=self.topic)
        comment_b = utils.create_comment(user=self.user2, topic=self.topic)
        comment_c = utils.create_comment(user=self.user2, topic=self.topic)

        Comment.objects.filter(pk=comment_a.pk).update(date=timezone.now() - datetime.timedelta(days=10))
        Comment.objects.filter(pk=comment_c.pk).update(date=timezone.now() - datetime.timedelta(days=5))

        utils.login(self)
        response = self.client.get(reverse("spirit:user:detail", kwargs={'pk': self.user2.pk,
                                                                            'slug': self.user2.st.slug}))
        self.assertEqual(list(response.context['comments']), [comment_b, comment_c, comment_a])

    @override_djconfig(comments_per_page=1)
    def test_profile_comments_paginate(self):
        """
        profile user's comments paginated
        """
        utils.create_comment(user=self.user2, topic=self.topic)
        comment = utils.create_comment(user=self.user2, topic=self.topic)

        utils.login(self)
        response = self.client.get(reverse("spirit:user:detail", kwargs={'pk': self.user2.pk,
                                                                            'slug': self.user2.st.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['comments']), [comment, ])

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
        response = self.client.get(reverse("spirit:user:detail", kwargs={'pk': self.user2.pk,
                                                                            'slug': self.user2.st.slug}))
        self.assertEqual(list(response.context['comments']), [])

    def test_profile_comments_invalid_slug(self):
        """
        profile user's comments, invalid user slug
        """
        utils.login(self)
        response = self.client.get(reverse("spirit:user:detail", kwargs={'pk': self.user2.pk,
                                                                            'slug': "invalid"}))
        expected_url = reverse("spirit:user:detail", kwargs={'pk': self.user2.pk,
                                                                'slug': self.user2.st.slug})
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
        response = self.client.get(reverse("spirit:user:likes", kwargs={'pk': self.user2.pk,
                                                                           'slug': self.user2.st.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['comments']), [like.comment, ])
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

        CommentLike.objects.filter(pk=like_a.pk).update(date=timezone.now() - datetime.timedelta(days=10))
        CommentLike.objects.filter(pk=like_c.pk).update(date=timezone.now() - datetime.timedelta(days=5))

        utils.login(self)
        response = self.client.get(reverse("spirit:user:likes", kwargs={'pk': self.user2.pk,
                                                                           'slug': self.user2.st.slug}))
        self.assertEqual(list(response.context['comments']), [comment_b, comment_c, comment_a])

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
        response = self.client.get(reverse("spirit:user:likes", kwargs={'pk': self.user2.pk,
                                                                           'slug': self.user2.st.slug}))
        self.assertEqual(list(response.context['comments']), [])

    def test_profile_likes_invalid_slug(self):
        """
        profile user's likes, invalid user slug
        """
        utils.login(self)
        response = self.client.get(reverse("spirit:user:likes", kwargs={'pk': self.user2.pk,
                                                                           'slug': "invalid"}))
        expected_url = reverse("spirit:user:likes", kwargs={'pk': self.user2.pk,
                                                               'slug': self.user2.st.slug})
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
        response = self.client.get(reverse("spirit:user:likes", kwargs={'pk': self.user2.pk,
                                                                           'slug': self.user2.st.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['comments']), [like.comment, ])

    def test_profile_update(self):
        """
        profile update
        """
        utils.login(self)
        # get
        response = self.client.get(reverse('spirit:user:update'))
        self.assertEqual(response.status_code, 200)

        # post
        form_data = {'first_name': 'foo', 'last_name': 'bar',
                     'location': 'spirit', 'timezone': self.user.st.timezone}
        response = self.client.post(reverse('spirit:user:update'),
                                    form_data)
        expected_url = reverse('spirit:user:update')
        self.assertRedirects(response, expected_url, status_code=302)

    def test_login_rate_limit(self):
        """
        test rate limit 5/5m
        """
        form_data = {'username': self.user.email, 'password': "badpassword"}

        for attempt in range(5):
            url = reverse('spirit:user:auth:login')
            response = self.client.post(url, form_data)
            self.assertTemplateUsed(response, 'spirit/user/auth/login.html')

        url = reverse('spirit:user:auth:login') + "?next=/path/"
        response = self.client.post(url, form_data)
        self.assertRedirects(response, url, status_code=302)

    def test_custom_reset_password(self):
        """
        test rate limit 5/5m
        """
        form_data = {'email': "bademail@bad.com", }

        for attempt in range(5):
            response = self.client.post(reverse('spirit:user:auth:password-reset'), form_data)
            expected_url = reverse("spirit:user:auth:password-reset-done")
            self.assertRedirects(response, expected_url, status_code=302)

        response = self.client.post(reverse('spirit:user:auth:password-reset'), form_data)
        expected_url = reverse("spirit:user:auth:password-reset")
        self.assertRedirects(response, expected_url, status_code=302)

    def test_password_reset_confirm(self):
        """
        test access
        """
        response = self.client.get(reverse('spirit:user:auth:password-reset-confirm', kwargs={'uidb64': 'f-a-k-e',
                                                                                    'token': 'f-a-k-e'}))
        self.assertEqual(response.status_code, 200)

    def test_admin_login(self):
        """
        Redirect to regular user login (optional)
        make sure you added:
        admin.site.login = login_required(admin.site.login)
        to urls.py (the one in your project's root)
        """
        # TODO: document that devs should be doing this.
        try:
            url = reverse('admin:login')
        except NoReverseMatch:
            return

        response = self.client.get(url)
        expected_url = reverse("spirit:user:auth:login") + "?next=" + reverse('admin:login')
        self.assertRedirects(response, expected_url, status_code=302)

    def test_profile_password_change(self):
        """
        profile password change
        """
        user = utils.create_user(password="foo")
        utils.login(self, user=user, password="foo")
        form_data = {'old_password': 'foo',
                     'new_password1': 'bar',
                     'new_password2': 'bar'}
        response = self.client.post(reverse('spirit:user:password-change'),
                                    form_data)
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

        form_data = {'old_password': 'foo',
                     'new_password1': 'bar',
                     'new_password2': 'bar'}
        response = self.client.post(reverse('spirit:user:password-change'), form_data)
        expected_url = reverse("spirit:user:update")
        self.assertRedirects(response, expected_url, status_code=302)

        self.assertNotEqual(old_hash, self.client.session[HASH_SESSION_KEY])

    def test_registration_activation(self):
        """
        registration activation
        """
        self.user.st.is_verified = False
        self.user.is_active = False
        self.user.save()
        token = UserActivationTokenGenerator().generate(self.user)
        response = self.client.get(reverse('spirit:user:auth:registration-activation', kwargs={'pk': self.user.pk,
                                                                                     'token': token}))
        expected_url = reverse("spirit:user:auth:login")
        self.assertRedirects(response, expected_url, status_code=302)
        self.assertTrue(User.objects.get(pk=self.user.pk).is_active)

    def test_registration_activation_invalid(self):
        """
        Activation token should not work if user is verified
        ActiveUserMiddleware required
        """
        self.user.st.is_verified = False
        token = UserActivationTokenGenerator().generate(self.user)

        utils.login(self)
        User.objects.filter(pk=self.user.pk).update(is_active=False)
        UserProfile.objects.filter(user__pk=self.user.pk).update(is_verified=True)
        response = self.client.get(reverse('spirit:user:auth:registration-activation', kwargs={'pk': self.user.pk,
                                                                                     'token': token}))
        expected_url = reverse("spirit:user:auth:login")
        self.assertRedirects(response, expected_url, status_code=302)
        self.assertFalse(User.objects.get(pk=self.user.pk).is_active)

    def test_email_change_confirm(self):
        """
        email change confirmation
        """
        utils.login(self)
        new_email = "newfoo@bar.com"
        token = UserEmailChangeTokenGenerator().generate(self.user, new_email)
        response = self.client.get(reverse('spirit:user:email-change-confirm', kwargs={'token': token}))
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
        response = self.client.get(reverse('spirit:user:email-change-confirm', kwargs={'token': token}))
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
        self.client.get(reverse('spirit:user:email-change-confirm', kwargs={'token': token}))
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
        self.client.get(reverse('spirit:user:email-change-confirm', kwargs={'token': token}))
        self.assertEqual(User.objects.get(pk=self.user.pk).email, new_email)

    def test_profile_email_change(self):
        """
        email change
        """
        user = utils.create_user(password="foo")
        utils.login(self, user=user, password="foo")
        form_data = {'password': 'foo',
                     'email': 'newfoo@bar.com'}
        response = self.client.post(reverse('spirit:user:email-change'),
                                    form_data)
        expected_url = reverse("spirit:user:update")
        self.assertRedirects(response, expected_url, status_code=302)
        self.assertEquals(len(mail.outbox), 1)
        self.assertIn(_("Email change"), mail.outbox[0].subject)

        # get
        response = self.client.get(reverse('spirit:user:email-change'))
        self.assertEqual(response.status_code, 200)

    def test_resend_activation_email(self):
        """
        resend_activation_email
        """
        user = utils.create_user(password="foo")

        form_data = {'email': user.email,
                     'password': "foo"}
        response = self.client.post(reverse('spirit:user:auth:resend-activation'),
                                    form_data)
        expected_url = reverse("spirit:user:auth:login")
        self.assertRedirects(response, expected_url, status_code=302)
        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].subject, _("User activation"))

        # get
        response = self.client.get(reverse('spirit:user:auth:resend-activation'))
        self.assertEquals(response.status_code, 200)

    def test_resend_activation_email_invalid_previously_logged_in(self):
        """
        resend_activation_email invalid if is_verified was set
        """
        user = utils.create_user(password="foo")
        user.st.is_verified = True
        user.st.save()

        form_data = {'email': user.email,
                     'password': "foo"}
        response = self.client.post(reverse('spirit:user:auth:resend-activation'),
                                    form_data)
        self.assertEquals(response.status_code, 302)
        self.assertEquals(len(mail.outbox), 0)

    def test_resend_activation_email_invalid_email(self):
        """
        resend_activation_email invalid password
        """
        utils.create_user(password="foo")

        form_data = {'email': "bad@foo.com", }
        response = self.client.post(reverse('spirit:user:auth:resend-activation'),
                                    form_data)
        self.assertEquals(response.status_code, 302)
        self.assertEquals(len(mail.outbox), 0)

    def test_resend_activation_email_redirect_logged(self):
        """
        resend_activation_email redirect to profile if user is logged in
        """
        utils.login(self)
        response = self.client.get(reverse('spirit:user:auth:resend-activation'))
        expected_url = reverse("spirit:user:update")
        self.assertRedirects(response, expected_url, status_code=302)

    def test_logout(self):
        """
        should log out on POST only
        """
        utils.login(self)

        # get should display confirmation message
        response = self.client.get(reverse('spirit:user:auth:logout'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.client.session.items())

        # post should log out the user (clear the session)
        response = self.client.post(reverse('spirit:user:auth:logout'))
        expected_url = "/"
        self.assertRedirects(response, expected_url, status_code=302)
        self.assertFalse(self.client.session.items())

        # next
        utils.login(self)
        self.assertTrue(self.client.session.items())
        response = self.client.post(reverse('spirit:user:auth:logout') + '?next=/fakepath/')
        self.assertRedirects(response, '/fakepath/', status_code=302, target_status_code=404)
        self.assertFalse(self.client.session.items())

    def test_logout_anonymous_redirect(self):
        """
        should log out on POST only
        """
        # redirect to login if user is anonymous
        response = self.client.get(reverse('spirit:user:auth:logout'))
        expected_url = reverse("spirit:user:auth:login")
        self.assertRedirects(response, expected_url, status_code=302)

        # next if user is anonymous
        response = self.client.get(reverse('spirit:user:auth:logout') + '?next=/fakepath/')
        self.assertRedirects(response, '/fakepath/', status_code=302, target_status_code=404)


class UserFormTest(TestCase):

    def setUp(self):
        cache.clear()
        self.user = utils.create_user()

    def test_registration(self):
        """
        register
        """
        form_data = {'username': 'foo', 'email': 'foo@foo.com',
                     'password1': 'pass', 'password2': 'pass'}
        form = RegistrationForm(data=form_data)
        self.assertEqual(form.is_valid(), True)

    def test_registration_invalid(self):
        """
        invalid email and user
        """
        User.objects.create_user(username="foo", password="bar", email="foo@foo.com")
        form_data = {'username': 'foo', 'email': 'foo@foo.com',
                     'password1': 'pass', 'password2': 'pass'}
        form = RegistrationForm(data=form_data)
        self.assertEqual(form.is_valid(), False)
        self.assertNotIn('username', form.cleaned_data)
        self.assertNotIn('foo@foo.com', form.cleaned_data)

    def test_registration_honeypot(self):
        """
        registration honeypot
        """
        form_data = {'username': 'foo', 'email': 'foo@foo.com',
                     'password1': 'pass', 'password2': 'pass',
                     'honeypot': 'im a robot'}
        form = RegistrationForm(data=form_data)
        self.assertEqual(form.is_valid(), False)
        self.assertNotIn('honeypot', form.cleaned_data)

    def test_registration_email_duplication(self):
        """
        register, don't allow email duplication
        """
        utils.create_user(email='duplicated@bar.com')
        form_data = {'username': 'foo', 'email': 'duplicated@bar.com',
                     'password1': 'pass', 'password2': 'pass'}
        form = RegistrationForm(data=form_data)
        self.assertEqual(form.is_valid(), False)
        self.assertNotIn('email', form.cleaned_data)

    @override_settings(ST_UNIQUE_EMAILS=False)
    def test_registration_email_duplication_allowed(self):
        """
        Duplicated email allowed
        """
        utils.create_user(email='duplicated@bar.com')
        form_data = {'username': 'foo', 'email': 'duplicated@bar.com',
                     'password1': 'pass', 'password2': 'pass'}
        form = RegistrationForm(data=form_data)
        self.assertEqual(form.is_valid(), True)

    def test_profile(self):
        """
        edit user profile
        """
        form_data = {'first_name': 'foo', 'last_name': 'bar',
                     'location': 'spirit', 'timezone': self.user.st.timezone}
        form = UserProfileForm(data=form_data, instance=self.user.st)
        self.assertEqual(form.is_valid(), True)

        form = UserForm(data=form_data, instance=self.user)
        self.assertEqual(form.is_valid(), True)

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

    def test_resend_activation_email(self):
        """
        resend activation
        """
        user = utils.create_user(email="newfoo@bar.com")
        form_data = {'email': 'newfoo@bar.com', }
        form = ResendActivationForm(form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.get_user(), user)

    def test_resend_activation_email_invalid_email(self):
        """
        resend activation invalid
        """
        form_data = {'email': 'bad@bar.com', }
        form = ResendActivationForm(form_data)
        self.assertFalse(form.is_valid())

    def test_resend_activation_email_duplication(self):
        """
        Send email to the first *not verified* user found
        """
        utils.create_user(email="duplicated@bar.com")
        user2 = utils.create_user(email="duplicated@bar.com")
        user3 = utils.create_user(email="duplicated@bar.com")
        form_data = {'email': 'duplicated@bar.com', }
        form = ResendActivationForm(form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.get_user(), user3)

        user3.st.is_verified = True
        user3.st.save()
        form = ResendActivationForm(form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.get_user(), user2)

    def test_email_check(self):
        """
        Check it's an email
        """
        # Unique email
        form_data = {'email': 'unique@bar.com', }
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


class UserBackendTest(TestCase):

    def setUp(self):
        cache.clear()
        self.user = utils.create_user(email="foobar@bar.com", password="bar")

    def test_email_auth_backend(self):
        user = EmailAuthBackend().authenticate(username="foobar@bar.com", password="bar")
        self.assertEqual(user, self.user)

    def test_email_auth_backend_email_duplication(self):
        """
        it should NOT authenticate when the email is not unique (current behaviour, sorry)
        """
        utils.create_user(email="duplicated@bar.com", password="foo")
        utils.create_user(email="duplicated@bar.com", password="foo2")
        user = EmailAuthBackend().authenticate(username="duplicated@bar.com", password="foo")
        self.assertIsNone(user)


class UserModelTest(TestCase):

    def setUp(self):
        cache.clear()

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
