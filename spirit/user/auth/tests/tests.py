# -*- coding: utf-8 -*-

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail
from django.utils.translation import gettext as _
from django.test.utils import override_settings
from django.urls import NoReverseMatch

from spirit.core.tests import utils
from ..forms import RegistrationForm, ResendActivationForm, LoginForm
from ..backends import EmailAuthBackend, UsernameAuthBackend
from ...utils.tokens import UserActivationTokenGenerator
from ...models import UserProfile
from .urls import CustomRegisterForm

User = get_user_model()


class UserViewTest(TestCase):

    def setUp(self):
        utils.cache_clear()
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

    def test_login_open_redirect(self):
        utils.login(self)
        response = self.client.get(reverse('spirit:user:auth:login') + '?next=https%3A%2F%2Fevil.com')
        self.assertRedirects(response, '/', status_code=302)

    @override_settings(ST_CASE_INSENSITIVE_EMAILS=True)
    def test_login_email_case_insensitive(self):
        """
        try to login by email
        """
        self.assertNotEqual(
            self.user.email, self.user.email.upper())
        form_data = {
            'username': self.user.email.upper(),
            'password': "bar"}
        response = self.client.post(
            reverse('spirit:user:auth:login'), form_data)
        expected_url = reverse('spirit:user:update')
        self.assertRedirects(response, expected_url, status_code=302)

    @override_settings(ST_CASE_INSENSITIVE_EMAILS=False)
    def test_login_email_case_insensitive_off(self):
        """
        try to login by email
        """
        self.assertNotEqual(
            self.user.email, self.user.email.upper())
        form_data = {
            'username': self.user.email.upper(),
            'password': "bar"}
        response = self.client.post(
            reverse('spirit:user:auth:login'), form_data)
        self.assertEqual(response.status_code, 200)

    @override_settings(ST_CASE_INSENSITIVE_USERNAMES=True)
    def test_login_username_case_insensitive(self):
        self.assertNotEqual(
            self.user.username, self.user.username.upper())
        form_data = {
            'username': self.user.username.upper(),
            'password': "bar"}
        response = self.client.post(
            reverse('spirit:user:auth:login'), form_data)
        expected_url = reverse('spirit:user:update')
        self.assertRedirects(response, expected_url, status_code=302)

    @override_settings(ST_CASE_INSENSITIVE_USERNAMES=False)
    def test_login_username_case_insensitive_off(self):
        self.assertNotEqual(
            self.user.username, self.user.username.upper())
        form_data = {
            'username': self.user.username.upper(),
            'password': "bar"}
        response = self.client.post(
            reverse('spirit:user:auth:login'), form_data)
        self.assertEqual(response.status_code, 200)

    def test_register(self):
        """
        register
        """
        # get
        response = self.client.get(reverse('spirit:user:auth:register'))
        self.assertEqual(response.status_code, 200)

        # post
        form_data = {'username': 'uniquefoo', 'email': 'some@some.com',
                     'email2': 'some@some.com', 'password': 'pass'}
        response = self.client.post(reverse('spirit:user:auth:register'),
                                    form_data)
        expected_url = reverse('spirit:user:auth:login')
        self.assertRedirects(response, expected_url, status_code=302)

        # redirect logged in user
        utils.login(self)
        response = self.client.get(reverse('spirit:user:auth:register'))
        self.assertRedirects(response, reverse('spirit:user:update'), status_code=302)

    @override_settings(ST_CASE_INSENSITIVE_USERNAMES=True)
    def test_register_username_case_insensitive(self):
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
            User.objects.filter(username='uniquefoo').exists())
        self.assertFalse(
            User.objects.filter(username='UnIqUeFoO').exists())

    @override_settings(ST_CASE_INSENSITIVE_USERNAMES=False)
    def test_register_username_case_insensitive_off(self):
        form_data = {
            'username': 'UnIqUeFoO',
            'email': 'some@some.com',
            'email2': 'some@some.com',
            'password': 'pass'}
        response = self.client.post(
            reverse('spirit:user:auth:register'), form_data)
        expected_url = reverse('spirit:user:auth:login')
        self.assertRedirects(response, expected_url, status_code=302)
        self.assertFalse(
            User.objects.filter(username='uniquefoo').exists())
        self.assertTrue(
            User.objects.filter(username='UnIqUeFoO').exists())

    @utils.immediate_on_commit
    def test_register_email_sent(self):
        """
        register and send activation email
        """
        form_data = {'username': 'uniquefoo', 'email': 'some@some.com',
                     'email2': 'some@some.com', 'password': 'pass'}
        response = self.client.post(reverse('spirit:user:auth:register'), form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, _("User activation"))

    def test_register_next_logged_in(self):
        """
        redirect next on register
        """
        # redirect logged in user
        utils.login(self)
        response = self.client.get(reverse('spirit:user:auth:register') + "?next=/fakepath/")
        self.assertRedirects(response, '/fakepath/', status_code=302, target_status_code=404)

    @override_settings(ROOT_URLCONF='spirit.user.auth.tests.urls')
    def test_register_custom_form(self):
        """
        Should allow a custom form
        """
        response = self.client.get(reverse('spirit:user:auth:register'))
        self.assertIsInstance(response.context['form'], CustomRegisterForm)

        response = self.client.post(reverse('spirit:user:auth:register'), {})
        self.assertIsInstance(response.context['form'], CustomRegisterForm)

    @override_settings(ST_TESTS_RATELIMIT_NEVER_EXPIRE=True)
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

    @override_settings(ST_TESTS_RATELIMIT_NEVER_EXPIRE=True)
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

    @utils.immediate_on_commit
    def test_custom_reset_password_email(self):
        self.assertEqual(len(mail.outbox), 0)
        form_data = {'email': self.user.email}
        response = self.client.post(
            reverse('spirit:user:auth:password-reset'), form_data)
        expected_url = reverse("spirit:user:auth:password-reset-done")
        self.assertRedirects(response, expected_url, status_code=302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Password reset on", mail.outbox[0].subject)
        self.assertIn("you requested a password reset", mail.outbox[0].body)
        self.assertEqual(mail.outbox[0].to, [self.user.email])

    def test_password_reset_confirm(self):
        """
        test access
        """
        response = self.client.get(
            reverse(
                'spirit:user:auth:password-reset-confirm',
                kwargs={'uidb64': 'f-a-k-e', 'token': 'f-a-k-e'}
            )
        )
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

    def test_registration_activation(self):
        """
        registration activation
        """
        self.user.st.is_verified = False
        self.user.is_active = False
        self.user.save()
        token = UserActivationTokenGenerator().generate(self.user)
        response = self.client.get(
            reverse(
                'spirit:user:auth:registration-activation',
                kwargs={'pk': self.user.pk, 'token': token}
            )
        )
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
        response = self.client.get(
            reverse(
                'spirit:user:auth:registration-activation',
                kwargs={'pk': self.user.pk, 'token': token}
            )
        )
        expected_url = reverse("spirit:user:auth:login")
        self.assertRedirects(response, expected_url, status_code=302)
        self.assertFalse(User.objects.get(pk=self.user.pk).is_active)

    @utils.immediate_on_commit
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
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, _("User activation"))

        # get
        response = self.client.get(reverse('spirit:user:auth:resend-activation'))
        self.assertEqual(response.status_code, 200)

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
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 0)

    def test_resend_activation_email_invalid_email(self):
        """
        resend_activation_email invalid password
        """
        utils.create_user(password="foo")

        form_data = {'email': "bad@foo.com", }
        response = self.client.post(reverse('spirit:user:auth:resend-activation'),
                                    form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 0)

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
        utils.cache_clear()
        self.user = utils.create_user()

    def test_registration(self):
        """
        register
        """
        form_data = {'username': 'foo', 'email': 'foo@foo.com',
                     'email2': 'foo@foo.com', 'password': 'pass'}
        form = RegistrationForm(data=form_data)
        self.assertEqual(form.is_valid(), True)

    def test_registration_login(self):
        """
        Register and login
        """
        form_data = {'username': 'foo', 'email': 'foo@foo.com',
                     'email2': 'foo@foo.com', 'password': 'pass'}
        form = RegistrationForm(data=form_data)
        self.assertEqual(form.is_valid(), True)

        user = form.save()
        self.assertFalse(user.is_active)

        user.is_active = True
        user.save()
        utils.login(self, user=user, password='pass')  # Asserts if can't login

    def test_registration_email_required(self):
        """
        Registration should require the email field
        """
        form_data = {'username': 'foo',
                     'password': 'pass'}
        form = RegistrationForm(data=form_data)
        self.assertEqual(form.is_valid(), False)
        self.assertIn('email', form.errors)

    def test_registration_invalid(self):
        """
        invalid email and user
        """
        User.objects.create_user(username="foo", password="bar", email="foo@foo.com")
        form_data = {'username': 'foo', 'email': 'foo@foo.com',
                     'email2': 'foo@foo.com', 'password': 'pass'}
        form = RegistrationForm(data=form_data)
        self.assertEqual(form.is_valid(), False)
        self.assertNotIn('username', form.cleaned_data)
        self.assertNotIn('foo@foo.com', form.cleaned_data)

    def test_registration_honeypot(self):
        """
        registration honeypot
        """
        form_data = {'username': 'foo', 'email': 'foo@foo.com',
                     'email2': 'foo@foo.com', 'password': 'pass',
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
                     'email2': 'duplicated@bar.com', 'password': 'pass'}
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
                     'email2': 'duplicated@bar.com', 'password': 'pass'}
        form = RegistrationForm(data=form_data)
        self.assertEqual(form.is_valid(), True)

    def test_registration_email_confirmation(self):
        """
        Confirmation email should match email
        """
        form_data = {'username': 'foo', 'email': 'foo@bar.com',
                     'email2': 'foofoo@bar.com', 'password': 'pass'}
        form = RegistrationForm(data=form_data)
        self.assertEqual(form.is_valid(), False)
        self.assertNotIn('email2', form.cleaned_data)

    @override_settings(ST_CASE_INSENSITIVE_EMAILS=True)
    def test_registration_email_confirmation_case_insensitive(self):
        """
        Confirmation email should match email
        """
        form_data = {'username': 'foo', 'email': 'FOO@bar.com',
                     'email2': 'FOO@BAR.COM', 'password': 'pass'}
        form = RegistrationForm(data=form_data)
        self.assertEqual(form.is_valid(), True)

    @override_settings(ST_CASE_INSENSITIVE_EMAILS=False)
    def test_registration_email_confirmation_case_sensitive(self):
        """
        Confirmation email should match email
        """
        form_data = {'username': 'foo', 'email': 'FOO@bar.com',
                     'email2': 'FOO@BAR.COM', 'password': 'pass'}
        form = RegistrationForm(data=form_data)
        self.assertEqual(form.is_valid(), False)
        self.assertNotIn('email2', form.cleaned_data)

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

    @override_settings(ST_CASE_INSENSITIVE_EMAILS=True)
    def test_resend_activation_email_case_insensitive(self):
        """
        Should lower the email before checking it
        """
        user = utils.create_user(email="newfoo@bar.com")
        form_data = {'email': 'NeWfOO@bAr.COM', }
        form = ResendActivationForm(form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.get_user(), user)

    @override_settings(ST_CASE_INSENSITIVE_EMAILS=False)
    def test_resend_activation_email_case_sensitive(self):
        """
        Should NOT lower the email before checking it
        """
        utils.create_user(email="newfoo@bar.com")
        form_data = {'email': 'NeWfOO@bAr.COM', }
        form = ResendActivationForm(form_data)
        self.assertFalse(form.is_valid())
        self.assertRaises(AttributeError, form.get_user)

    def test_login(self):
        """
        Should login the user
        """
        utils.create_user(username="foobar", password="foo")
        form_data = {'username': "foobar", 'password': "foo"}
        form = LoginForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_login_email(self):
        """
        Should login the user by email
        """
        utils.create_user(email="foobar@bar.com", password="foo")
        form_data = {'username': "foobar@bar.com", 'password': "foo"}
        form = LoginForm(data=form_data)
        self.assertTrue(form.is_valid())

    @override_settings(ST_CASE_INSENSITIVE_EMAILS=False)
    def test_login_email_case_sensitive(self):
        """
        Should login the user by email
        """
        utils.create_user(email="foobar@bar.com", password="foo")
        form_data = {'username': "FOOBAR@bar.com", 'password': "foo"}
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())

    @override_settings(ST_CASE_INSENSITIVE_EMAILS=True)
    def test_login_email_case_sensitive(self):
        """
        Should login the user by email
        """
        utils.create_user(email="foobar@bar.com", password="foo")
        form_data = {'username': "FOOBAR@bar.com", 'password': "foo"}
        form = LoginForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_login_invalid(self):
        """
        Should not login invalid user
        """
        form = LoginForm(data={})
        self.assertFalse(form.is_valid())

    def test_login_password_invalid(self):
        """
        Should not login invalid user
        """
        utils.create_user(username="foobar", password="foo")
        form_data = {'username': "foobar", 'password': "bad"}
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_login_username_invalid(self):
        """
        Should not login invalid user
        """
        utils.create_user(username="foobar", password="foo")
        form_data = {'username': "bad", 'password': "foo"}
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())


class UserBackendTest(TestCase):

    def setUp(self):
        utils.cache_clear()
        self.user = utils.create_user(
            email="foobar@bar.com",
            password="bar")

    def test_email_auth_backend(self):
        user = EmailAuthBackend().authenticate(
            request=None, username="foobar@bar.com", password="bar")
        self.assertEqual(user, self.user)

    def test_email_auth_backend_email_duplication(self):
        """
        it should NOT authenticate when the email is not unique (current behaviour, sorry)
        """
        utils.create_user(email="duplicated@bar.com", password="foo")
        utils.create_user(email="duplicated@bar.com", password="foo2")
        user = EmailAuthBackend().authenticate(
            request=None, username="duplicated@bar.com", password="foo")
        self.assertIsNone(user)

    @override_settings(ST_CASE_INSENSITIVE_EMAILS=True)
    def test_email_auth_backend_case_insensitive(self):
        user = EmailAuthBackend().authenticate(
            request=None, username="FooBar@bAr.COM", password="bar")
        self.assertEqual(user, self.user)

    @override_settings(ST_CASE_INSENSITIVE_EMAILS=False)
    def test_email_auth_backend_case_sensitive(self):
        user = EmailAuthBackend().authenticate(
            request=None, username="FooBar@bAr.COM", password="bar")
        self.assertIsNone(user)

    @override_settings(ST_CASE_INSENSITIVE_USERNAMES=True)
    def test_username_auth_backend_case_sensitive(self):
        usr = utils.create_user(
            username="FooBar",
            password="bar")
        user = UsernameAuthBackend().authenticate(
            request=None, username="FooBar", password="bar")
        self.assertEqual(user.pk, usr.pk)
        user = UsernameAuthBackend().authenticate(
            request=None, username="foobar", password="bar")
        self.assertEqual(user.pk, usr.pk)

    @override_settings(ST_CASE_INSENSITIVE_USERNAMES=False)
    def test_username_auth_backend_case_sensitive_off(self):
        usr = utils.create_user(
            username="FooBar",
            password="bar")
        user = UsernameAuthBackend().authenticate(
            request=None, username="FooBar", password="bar")
        self.assertEqual(user.pk, usr.pk)
        user = UsernameAuthBackend().authenticate(
            request=None, username="foobar", password="bar")
        self.assertIsNone(user)
