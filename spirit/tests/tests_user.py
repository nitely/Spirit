#-*- coding: utf-8 -*-

import datetime

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.template import Template, Context, TemplateSyntaxError
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.core import mail
from django.utils.translation import ugettext as _
from django.utils import timezone

import utils

from spirit.forms.user import RegistrationForm, UserProfileForm, EmailChangeForm, ResendActivationForm
from spirit.backends.user import EmailAuthBackend
from spirit.models.comment_like import CommentLike
from spirit.utils.user.tokens import UserActivationTokenGenerator, UserEmailChangeTokenGenerator
from spirit.models.user import User as UserModel
from spirit.models.topic import Topic
from spirit.models.comment import Comment


User = get_user_model()


class UserViewTest(TestCase):

    fixtures = ['spirit_init.json', ]

    def setUp(self):
        cache.clear()
        self.user = utils.create_user()
        self.user2 = utils.create_user()
        self.category = utils.create_category()
        self.topic = utils.create_topic(self.category, user=self.user2)
        self.topic2 = utils.create_topic(self.category)

    def test_login_email(self):
        """
        try to login by email
        """
        # get
        response = self.client.get(reverse('spirit:user-login'))
        self.assertEqual(response.status_code, 200)

        # post
        form_data = {'username': self.user.email, 'password': "bar"}
        response = self.client.post(reverse('spirit:user-login'),
                                    form_data)
        expected_url = reverse('spirit:profile-update')
        self.assertRedirects(response, expected_url, status_code=302)

    def test_login_redirect(self):
        """
        try to login with a logged in user
        """
        utils.login(self)
        response = self.client.get(reverse('spirit:user-login'))
        expected_url = self.user.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302)
        # next
        response = self.client.get(reverse('spirit:user-login') + '?next=/fakepath/')
        self.assertRedirects(response, '/fakepath/', status_code=302, target_status_code=404)

    def test_register(self):
        """
        register
        """
        # get
        response = self.client.get(reverse('spirit:user-register'))
        self.assertEqual(response.status_code, 200)

        # post
        form_data = {'username': 'uniquefoo', 'email': 'some@some.com', 'password1': 'pass', 'password2': 'pass'}
        response = self.client.post(reverse('spirit:user-register'),
                                    form_data)
        expected_url = reverse('spirit:user-login')
        self.assertRedirects(response, expected_url, status_code=302)

        # redirect logged in user
        utils.login(self)
        response = self.client.get(reverse('spirit:user-register'))
        self.assertRedirects(response, reverse('spirit:profile-update'), status_code=302)

    def test_register_email_sent(self):
        """
        register and send activation email
        """
        form_data = {'username': 'uniquefoo', 'email': 'some@some.com', 'password1': 'pass', 'password2': 'pass'}
        response = self.client.post(reverse('spirit:user-register'), form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].subject, _("User activation"))

    def test_register_next_logged_in(self):
        """
        redirect next on register
        """
        # redirect logged in user
        utils.login(self)
        response = self.client.get(reverse('spirit:user-register') + "?next=/fakepath/")
        self.assertRedirects(response, '/fakepath/', status_code=302, target_status_code=404)

    def test_profile_topics(self):
        """
        profile user's topics
        """
        utils.login(self)
        response = self.client.get(reverse("spirit:profile-topics", kwargs={'pk': self.user2.pk,
                                                                            'slug': self.user2.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['topics'], [repr(self.topic), ])
        self.assertEqual(repr(response.context['p_user']), repr(self.user2))

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
        response = self.client.get(reverse("spirit:profile-topics", kwargs={'pk': self.user2.pk,
                                                                            'slug': self.user2.slug}))
        self.assertQuerysetEqual(response.context['topics'], map(repr, [topic_b, topic_c, topic_a]))

    def test_profile_topics_dont_show_removed_or_private(self):
        """
        dont show private topics or removed
        """
        Topic.objects.all().delete()

        category = utils.create_category()
        category_removed = utils.create_category(is_removed=True)
        subcategory = utils.create_category(parent=category_removed)
        subcategory_removed = utils.create_category(parent=category, is_removed=True)
        topic_a = utils.create_private_topic(user=self.user2)
        topic_b = utils.create_topic(category=category, user=self.user2, is_removed=True)
        topic_c = utils.create_topic(category=category_removed, user=self.user2)
        topic_d = utils.create_topic(category=subcategory, user=self.user2)
        topic_e = utils.create_topic(category=subcategory_removed, user=self.user2)

        utils.login(self)
        response = self.client.get(reverse("spirit:profile-topics", kwargs={'pk': self.user2.pk,
                                                                            'slug': self.user2.slug}))
        self.assertQuerysetEqual(response.context['topics'], [])

    def test_profile_topics_invalid_slug(self):
        """
        profile user's topics
        """
        utils.login(self)
        response = self.client.get(reverse("spirit:profile-topics", kwargs={'pk': self.user2.pk,
                                                                            'slug': "invalid"}))
        expected_url = reverse("spirit:profile-topics", kwargs={'pk': self.user2.pk,
                                                                'slug': self.user2.slug})
        self.assertRedirects(response, expected_url, status_code=301)

    def test_profile_comments(self):
        """
        profile user's comments
        """
        utils.login(self)
        comment = utils.create_comment(user=self.user2, topic=self.topic)
        comment2 = utils.create_comment(user=self.user, topic=self.topic)
        response = self.client.get(reverse("spirit:profile-detail", kwargs={'pk': self.user2.pk,
                                                                            'slug': self.user2.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['comments'], [repr(comment), ])
        self.assertEqual(repr(response.context['p_user']), repr(self.user2))

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
        response = self.client.get(reverse("spirit:profile-detail", kwargs={'pk': self.user2.pk,
                                                                            'slug': self.user2.slug}))
        self.assertQuerysetEqual(response.context['comments'], map(repr, [comment_b, comment_c, comment_a]))

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
        comment_a = utils.create_comment(user=self.user2, topic=topic_a.topic)
        comment_b = utils.create_comment(user=self.user2, topic=topic_b)
        comment_c = utils.create_comment(user=self.user2, topic=topic_c)
        comment_d = utils.create_comment(user=self.user2, topic=topic_d)
        comment_e = utils.create_comment(user=self.user2, topic=topic_e)

        utils.login(self)
        response = self.client.get(reverse("spirit:profile-detail", kwargs={'pk': self.user2.pk,
                                                                            'slug': self.user2.slug}))
        self.assertQuerysetEqual(response.context['comments'], [])

    def test_profile_comments_invalid_slug(self):
        """
        profile user's comments, invalid user slug
        """
        utils.login(self)
        response = self.client.get(reverse("spirit:profile-detail", kwargs={'pk': self.user2.pk,
                                                                            'slug': "invalid"}))
        expected_url = reverse("spirit:profile-detail", kwargs={'pk': self.user2.pk,
                                                                'slug': self.user2.slug})
        self.assertRedirects(response, expected_url, status_code=301)

    def test_profile_likes(self):
        """
        profile user's likes
        """
        utils.login(self)
        comment = utils.create_comment(user=self.user, topic=self.topic)
        comment2 = utils.create_comment(user=self.user2, topic=self.topic)
        like = CommentLike.objects.create(user=self.user2, comment=comment)
        like2 = CommentLike.objects.create(user=self.user, comment=comment2)
        response = self.client.get(reverse("spirit:profile-likes", kwargs={'pk': self.user2.pk,
                                                                           'slug': self.user2.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['comments'], [repr(like.comment), ])
        self.assertEqual(repr(response.context['p_user']), repr(self.user2))

    def test_profile_likes_order(self):
        """
        comments ordered by date
        """
        comment_a = utils.create_comment(user=self.user, topic=self.topic)
        comment_b = utils.create_comment(user=self.user, topic=self.topic)
        comment_c = utils.create_comment(user=self.user, topic=self.topic)
        like_a = CommentLike.objects.create(user=self.user2, comment=comment_a)
        like_b = CommentLike.objects.create(user=self.user2, comment=comment_b)
        like_c = CommentLike.objects.create(user=self.user2, comment=comment_c)

        CommentLike.objects.filter(pk=like_a.pk).update(date=timezone.now() - datetime.timedelta(days=10))
        CommentLike.objects.filter(pk=like_c.pk).update(date=timezone.now() - datetime.timedelta(days=5))

        utils.login(self)
        response = self.client.get(reverse("spirit:profile-likes", kwargs={'pk': self.user2.pk,
                                                                           'slug': self.user2.slug}))
        self.assertQuerysetEqual(response.context['comments'], map(repr, [comment_b, comment_c, comment_a]))

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
        like_a = CommentLike.objects.create(user=self.user2, comment=comment_a)
        like_b = CommentLike.objects.create(user=self.user2, comment=comment_b)
        like_c = CommentLike.objects.create(user=self.user2, comment=comment_c)
        like_d = CommentLike.objects.create(user=self.user2, comment=comment_d)
        like_e = CommentLike.objects.create(user=self.user2, comment=comment_e)

        utils.login(self)
        response = self.client.get(reverse("spirit:profile-likes", kwargs={'pk': self.user2.pk,
                                                                            'slug': self.user2.slug}))
        self.assertQuerysetEqual(response.context['comments'], [])

    def test_profile_likes_invalid_slug(self):
        """
        profile user's likes, invalid user slug
        """
        utils.login(self)
        response = self.client.get(reverse("spirit:profile-likes", kwargs={'pk': self.user2.pk,
                                                                           'slug': "invalid"}))
        expected_url = reverse("spirit:profile-likes", kwargs={'pk': self.user2.pk,
                                                               'slug': self.user2.slug})
        self.assertRedirects(response, expected_url, status_code=301)

    def test_profile_update(self):
        """
        profile update
        """
        utils.login(self)
        # get
        response = self.client.get(reverse('spirit:profile-update'))
        self.assertEqual(response.status_code, 200)

        # post
        form_data = {'first_name': 'foo', 'last_name': 'bar',
                     'location': 'spirit', 'timezone': self.user.timezone}
        response = self.client.post(reverse('spirit:profile-update'),
                                    form_data)
        expected_url = reverse('spirit:profile-update')
        self.assertRedirects(response, expected_url, status_code=302)

    def test_login_rate_limit(self):
        """
        test rate limit 5/5m
        """
        form_data = {'username': self.user.email, 'password': "badpassword"}
        url = reverse('spirit:user-login') + "?next=/path/"
        for _ in xrange(6):
            response = self.client.post(url, form_data)
        self.assertRedirects(response, url, status_code=302)

    def test_custom_reset_password(self):
        """
        test rate limit 5/5m
        """
        form_data = {'email': "bademail@bad.com", }
        for _ in xrange(6):
            response = self.client.post(reverse('spirit:password-reset'),
                                        form_data)
        expected_url = reverse("spirit:password-reset")
        self.assertRedirects(response, expected_url, status_code=302)

    def test_password_reset_confirm(self):
        """
        test access
        """
        response = self.client.get(reverse('spirit:password-reset-confirm', kwargs={'uidb64': 'f-a-k-e',
                                                                                    'token': 'f-a-k-e'}))
        self.assertEqual(response.status_code, 200)

    def test_admin_login(self):
        """
        redirect to regular user login
        if fails, make sure you added:
        admin.site.login = login_required(admin.site.login)
        to urls.py (the one in your project's root)
        """
        response = self.client.get(reverse('admin:index'))
        expected_url = reverse("spirit:user-login") + "?next=" + reverse('admin:index')
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
        response = self.client.post(reverse('spirit:profile-password-change'),
                                    form_data)
        expected_url = reverse("spirit:profile-update")
        self.assertRedirects(response, expected_url, status_code=302)
        utils.login(self, user=user, password="bar")

        # get
        response = self.client.get(reverse('spirit:profile-password-change'))
        self.assertEqual(response.status_code, 200)

    def test_registration_activation(self):
        """
        registration activation
        """
        self.user.is_active = False
        self.user.save()
        token = UserActivationTokenGenerator().generate(self.user)
        response = self.client.get(reverse('spirit:registration-activation', kwargs={'pk': self.user.pk,
                                                                                     'token': token}))
        expected_url = reverse("spirit:user-login")
        self.assertRedirects(response, expected_url, status_code=302)
        self.assertTrue(User.objects.get(pk=self.user.pk).is_active)

    def test_registration_activation_invalid(self):
        """
        Activation token should expire after first login
        ActiveUserMiddleware required
        """
        self.user.last_login = self.user.last_login - datetime.timedelta(hours=1)
        token = UserActivationTokenGenerator().generate(self.user)

        utils.login(self)
        User.objects.filter(pk=self.user.pk).update(is_active=False)
        response = self.client.get(reverse('spirit:registration-activation', kwargs={'pk': self.user.pk,
                                                                                     'token': token}))
        expected_url = reverse("spirit:user-login")
        self.assertRedirects(response, expected_url, status_code=302)
        self.assertFalse(User.objects.get(pk=self.user.pk).is_active)

    def test_email_change_confirm(self):
        """
        email change confirmation
        """
        utils.login(self)
        new_email = "newfoo@bar.com"
        token = UserEmailChangeTokenGenerator().generate(self.user, new_email)
        response = self.client.get(reverse('spirit:email-change-confirm', kwargs={'token': token}))
        expected_url = reverse("spirit:profile-update")
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
        response = self.client.get(reverse('spirit:email-change-confirm', kwargs={'token': token}))
        expected_url = reverse("spirit:profile-update")
        self.assertRedirects(response, expected_url, status_code=302)
        self.assertEqual(User.objects.get(pk=self.user.pk).email, new_email)

    def test_profile_email_change(self):
        """
        email change
        """
        user = utils.create_user(password="foo")
        utils.login(self, user=user, password="foo")
        form_data = {'password': 'foo',
                     'email': 'newfoo@bar.com'}
        response = self.client.post(reverse('spirit:profile-email-change'),
                                    form_data)
        expected_url = reverse("spirit:profile-update")
        self.assertRedirects(response, expected_url, status_code=302)
        self.assertEquals(len(mail.outbox), 1)
        self.assertIn(_("Email change"), mail.outbox[0].subject)

        # get
        response = self.client.get(reverse('spirit:profile-email-change'))
        self.assertEqual(response.status_code, 200)

    def test_resend_activation_email(self):
        """
        resend_activation_email
        """
        user = utils.create_user(password="foo")

        form_data = {'email': user.email,
                     'password': "foo"}
        response = self.client.post(reverse('spirit:resend-activation'),
                                    form_data)
        expected_url = reverse("spirit:user-login")
        self.assertRedirects(response, expected_url, status_code=302)
        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].subject, _("User activation"))

        # get
        response = self.client.get(reverse('spirit:resend-activation'))
        self.assertEquals(response.status_code, 200)

    def test_resend_activation_email_invalid_previously_logged_in(self):
        """
        resend_activation_email invalid if last_ip was set
        """
        user = utils.create_user(password="foo", last_ip="1.1.1.1")

        form_data = {'email': user.email,
                     'password': "foo"}
        response = self.client.post(reverse('spirit:resend-activation'),
                                    form_data)
        self.assertEquals(response.status_code, 302)
        self.assertEquals(len(mail.outbox), 0)

    def test_resend_activation_email_invalid_email(self):
        """
        resend_activation_email invalid password
        """
        user = utils.create_user(password="foo")

        form_data = {'email': "bad@foo.com", }
        response = self.client.post(reverse('spirit:resend-activation'),
                                    form_data)
        self.assertEquals(response.status_code, 302)
        self.assertEquals(len(mail.outbox), 0)

    def test_resend_activation_email_redirect_logged(self):
        """
        resend_activation_email redirect to profile if user is logged in
        """
        utils.login(self)
        response = self.client.get(reverse('spirit:resend-activation'))
        expected_url = reverse("spirit:profile-update")
        self.assertRedirects(response, expected_url, status_code=302)

    def test_logout(self):
        """
        should log out on POST only
        """
        utils.login(self)

        # get should display confirmation message
        response = self.client.get(reverse('spirit:user-logout'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.client.session.items())

        # post should log out the user (clear the session)
        response = self.client.post(reverse('spirit:user-logout'))
        expected_url = "/"
        self.assertRedirects(response, expected_url, status_code=302)
        self.assertFalse(self.client.session.items())

        # next
        utils.login(self)
        self.assertTrue(self.client.session.items())
        response = self.client.post(reverse('spirit:user-logout') + '?next=/fakepath/')
        self.assertRedirects(response, '/fakepath/', status_code=302, target_status_code=404)
        self.assertFalse(self.client.session.items())

    def test_logout_anonymous_redirect(self):
        """
        should log out on POST only
        """
        # redirect to login if user is anonymous
        response = self.client.get(reverse('spirit:user-logout'))
        expected_url = reverse("spirit:user-login")
        self.assertRedirects(response, expected_url, status_code=302)

        # next if user is anonymous
        response = self.client.get(reverse('spirit:user-logout') + '?next=/fakepath/')
        self.assertRedirects(response, '/fakepath/', status_code=302, target_status_code=404)


class UserFormTest(TestCase):

    fixtures = ['spirit_init.json', ]

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

    def test_profile(self):
        """
        edit user profile
        """
        form_data = {'first_name': 'foo', 'last_name': 'bar',
                     'location': 'spirit', 'timezone': self.user.timezone}
        form = UserProfileForm(data=form_data, instance=self.user)
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


class UserBackendTest(TestCase):

    fixtures = ['spirit_init.json', ]

    def setUp(self):
        cache.clear()
        self.user = utils.create_user(email="foobar@bar.com", password="bar")

    def test_email_auth_backend(self):
        user = EmailAuthBackend().authenticate(username="foobar@bar.com", password="bar")
        self.assertEqual(user, self.user)


class UserModelTest(TestCase):

    fixtures = ['spirit_init.json', ]

    def setUp(self):
        cache.clear()

    def test_user_superuser(self):
        """
        is_superuser should always be is_administrator and is_moderator
        test model
        """
        user = UserModel(is_superuser=True)
        user.save()
        self.assertTrue(user.is_administrator)
        self.assertTrue(user.is_moderator)

    def test_user_administrator(self):
        """
        is_administrator should always be is_moderator
        """
        user = UserModel(is_administrator=True)
        user.save()
        self.assertTrue(user.is_moderator)