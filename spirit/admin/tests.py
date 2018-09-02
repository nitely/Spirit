# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model

from djconfig.utils import override_djconfig

from ..core.tests import utils
from ..admin.views import dashboard
from ..admin import views
from ..comment.flag.admin import views as flag_views
from ..topic.admin import views as topic_views
from ..user.admin import views as user_views
from ..comment.flag.models import CommentFlag, Flag
from ..admin.forms import BasicConfigForm
from ..comment.flag.admin.forms import CommentFlagForm
from ..user.admin.forms import UserForm, UserProfileForm

User = get_user_model()


class AdminViewTest(TestCase):

    def setUp(self):
        utils.cache_clear()
        self.user = utils.create_user()
        self.user.st.is_administrator = True
        self.user.st.save()
        self.category = utils.create_category()
        self.topic = utils.create_topic(self.category, user=self.user)

    def test_permission_denied_to_non_admin(self):
        req = RequestFactory().get('/')
        req.user = self.user
        req.user.st.is_administrator = False

        self.assertRaises(PermissionDenied, flag_views.closed, req)
        self.assertRaises(PermissionDenied, flag_views.opened, req)
        self.assertRaises(PermissionDenied, flag_views.detail, req)

        self.assertRaises(PermissionDenied, views.config_basic, req)

        self.assertRaises(PermissionDenied, dashboard, req)

        self.assertRaises(PermissionDenied, topic_views.deleted, req)
        self.assertRaises(PermissionDenied, topic_views.closed, req)
        self.assertRaises(PermissionDenied, topic_views.pinned, req)

        self.assertRaises(PermissionDenied, user_views.edit, req)
        self.assertRaises(PermissionDenied, user_views.index, req)
        self.assertRaises(PermissionDenied, user_views.index_admins, req)
        self.assertRaises(PermissionDenied, user_views.index_mods, req)
        self.assertRaises(PermissionDenied, user_views.index_unactive, req)

    def test_user_edit(self):
        """
        Edit user profile
        """
        utils.login(self)
        form_data = {"username": "fooedit", "email": "foo@bar.com", "location": "Bs As",
                     "timezone": "UTC", "is_administrator": True, "is_moderator": True, "is_active": True}
        response = self.client.post(reverse('spirit:admin:user:edit', kwargs={'user_id': self.user.pk, }),
                                    form_data)
        expected_url = reverse('spirit:admin:user:edit', kwargs={'user_id': self.user.pk, })
        self.assertRedirects(response, expected_url, status_code=302)

        response = self.client.get(reverse('spirit:admin:user:edit', kwargs={'user_id': self.user.pk, }))
        self.assertEqual(response.status_code, 200)

    def test_user_list(self):
        """
        List of all users
        """
        utils.login(self)
        response = self.client.get(reverse('spirit:admin:user:index'))
        self.assertEqual(list(response.context['users']), [self.user, ])

    @override_djconfig(topics_per_page=1)
    def test_user_list_paginate(self):
        """
        List of all users paginated
        """
        user2 = utils.create_user()

        utils.login(self)
        response = self.client.get(reverse('spirit:admin:user:index'))
        self.assertEqual(list(response.context['users']), [user2, ])

    def test_user_admins(self):
        """
        List of admins
        """
        utils.login(self)
        response = self.client.get(reverse('spirit:admin:user:index-admins'))
        self.assertEqual(list(response.context['users']), [self.user, ])

    @override_djconfig(topics_per_page=1)
    def test_user_admins_paginate(self):
        """
        List of admins paginated
        """
        user2 = utils.create_user()
        user2.st.is_administrator = True
        user2.st.save()

        utils.login(self)
        response = self.client.get(reverse('spirit:admin:user:index-admins'))
        self.assertEqual(list(response.context['users']), [user2, ])

    def test_user_mods(self):
        """
        List of mods
        """
        mod = utils.create_user()
        mod.st.is_moderator = True
        mod.st.save()

        utils.login(self)
        response = self.client.get(reverse('spirit:admin:user:index-mods'))
        self.assertEqual(list(response.context['users']), [mod, ])

    @override_djconfig(topics_per_page=1)
    def test_user_mods_paginate(self):
        """
        List of mods paginated
        """
        mod = utils.create_user()
        mod.st.is_moderator = True
        mod.st.save()

        mod2 = utils.create_user()
        mod2.st.is_moderator = True
        mod2.st.save()

        utils.login(self)
        response = self.client.get(reverse('spirit:admin:user:index-mods'))
        self.assertEqual(list(response.context['users']), [mod2, ])

    def test_user_unactive(self):
        """
        List of unactive
        """
        unactive = utils.create_user()
        User.objects.filter(pk=unactive.pk).update(is_active=False)
        utils.login(self)
        response = self.client.get(reverse('spirit:admin:user:index-unactive'))
        self.assertEqual(list(response.context['users']), [unactive, ])

    @override_djconfig(topics_per_page=1)
    def test_user_unactive_paginate(self):
        """
        List of unactive paginated
        """
        unactive = utils.create_user()
        User.objects.filter(pk=unactive.pk).update(is_active=False)
        unactive2 = utils.create_user()
        User.objects.filter(pk=unactive2.pk).update(is_active=False)

        utils.login(self)
        response = self.client.get(reverse('spirit:admin:user:index-unactive'))
        self.assertEqual(list(response.context['users']), [unactive2, ])

    def test_index_dashboard(self):
        utils.login(self)
        response = self.client.get(reverse('spirit:admin:topic:index'))
        self.assertEqual(response.status_code, 200)

    def test_topic_deleted(self):
        """
        Deleted topics
        """
        topic_ = utils.create_topic(self.category, is_removed=True)
        utils.login(self)
        response = self.client.get(reverse('spirit:admin:topic:deleted'))
        self.assertEqual(list(response.context['topics']), [topic_, ])

    @override_djconfig(topics_per_page=1)
    def test_topic_deleted_paginate(self):
        """
        Deleted topics paginated
        """
        utils.create_topic(self.category, is_removed=True)
        topic_ = utils.create_topic(self.category, is_removed=True)

        utils.login(self)
        response = self.client.get(reverse('spirit:admin:topic:deleted'))
        self.assertEqual(list(response.context['topics']), [topic_, ])

    def test_topic_closed(self):
        """
        Closed topics
        """
        topic_ = utils.create_topic(self.category, is_closed=True)
        utils.login(self)
        response = self.client.get(reverse('spirit:admin:topic:closed'))
        self.assertEqual(list(response.context['topics']), [topic_, ])

    @override_djconfig(topics_per_page=1)
    def test_topic_closed_paginate(self):
        """
        Closed topics paginated
        """
        utils.create_topic(self.category, is_closed=True)
        topic_ = utils.create_topic(self.category, is_closed=True)
        utils.login(self)
        response = self.client.get(reverse('spirit:admin:topic:closed'))
        self.assertEqual(list(response.context['topics']), [topic_, ])

    def test_topic_pinned(self):
        """
        Pinned topics
        """
        topic_ = utils.create_topic(self.category, is_pinned=True)
        utils.login(self)
        response = self.client.get(reverse('spirit:admin:topic:pinned'))
        self.assertEqual(list(response.context['topics']), [topic_, ])

    @override_djconfig(topics_per_page=1)
    def test_topic_pinned_paginate(self):
        """
        Pinned topics paginated
        """
        utils.create_topic(self.category, is_pinned=True)
        topic_ = utils.create_topic(self.category, is_pinned=True)
        utils.login(self)
        response = self.client.get(reverse('spirit:admin:topic:pinned'))
        self.assertEqual(list(response.context['topics']), [topic_, ])

    def test_config_basic(self):
        """
        Config
        """
        utils.login(self)
        form_data = {"site_name": "foo", "site_description": "bar", "comments_per_page": 10, "topics_per_page": 10}
        response = self.client.post(reverse('spirit:admin:config-basic'),
                                    form_data)
        expected_url = reverse('spirit:admin:config-basic')
        self.assertRedirects(response, expected_url, status_code=302)

        response = self.client.get(reverse('spirit:admin:config-basic'))
        self.assertEqual(response.status_code, 200)

    def test_flag_open(self):
        """
        Open flags
        """
        comment = utils.create_comment(topic=self.topic)
        comment2 = utils.create_comment(topic=self.topic)
        CommentFlag.objects.create(comment=comment2, is_closed=True)
        flag_ = CommentFlag.objects.create(comment=comment)

        utils.login(self)
        response = self.client.get(reverse('spirit:admin:flag:opened'))
        self.assertEqual(list(response.context['flags']), [flag_, ])

    @override_djconfig(comments_per_page=1)
    def test_flag_open_paginate(self):
        """
        Open flags paginated
        """
        comment = utils.create_comment(topic=self.topic)
        comment2 = utils.create_comment(topic=self.topic)
        CommentFlag.objects.create(comment=comment2)
        flag_ = CommentFlag.objects.create(comment=comment)

        utils.login(self)
        response = self.client.get(reverse('spirit:admin:flag:opened'))
        self.assertEqual(list(response.context['flags']), [flag_, ])

    def test_flag_closed(self):
        """
        Open flags
        """
        comment = utils.create_comment(topic=self.topic)
        comment2 = utils.create_comment(topic=self.topic)
        flag_closed = CommentFlag.objects.create(comment=comment2, is_closed=True)
        CommentFlag.objects.create(comment=comment)

        utils.login(self)
        response = self.client.get(reverse('spirit:admin:flag:closed'))
        self.assertEqual(list(response.context['flags']), [flag_closed, ])

    @override_djconfig(comments_per_page=1)
    def test_flag_open_paginate(self):
        """
        Open flags paginated
        """
        comment = utils.create_comment(topic=self.topic)
        comment2 = utils.create_comment(topic=self.topic)
        CommentFlag.objects.create(comment=comment2, is_closed=True)
        flag_closed = CommentFlag.objects.create(comment=comment, is_closed=True)

        utils.login(self)
        response = self.client.get(reverse('spirit:admin:flag:closed'))
        self.assertEqual(list(response.context['flags']), [flag_closed, ])

    def test_flag_detail(self):
        """
        flag detail
        """
        comment = utils.create_comment(topic=self.topic)
        comment_flag = CommentFlag.objects.create(comment=comment)
        flag_ = Flag.objects.create(comment=comment, user=self.user, reason=0)

        comment2 = utils.create_comment(topic=self.topic)
        CommentFlag.objects.create(comment=comment2)
        Flag.objects.create(comment=comment2, user=self.user, reason=0)

        utils.login(self)
        form_data = {"is_closed": True, }
        response = self.client.post(reverse('spirit:admin:flag:detail', kwargs={'pk': comment_flag.pk, }),
                                    form_data)
        expected_url = reverse('spirit:admin:flag:index')
        self.assertRedirects(response, expected_url, status_code=302)

        response = self.client.get(reverse('spirit:admin:flag:detail', kwargs={'pk': comment_flag.pk, }))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['flag'], comment_flag)
        self.assertEqual(list(response.context['flags']), [flag_, ])

    @override_djconfig(comments_per_page=1)
    def test_flag_detail_paginate(self):
        """
        flag detail paginated
        """
        user2 = utils.create_user()
        comment = utils.create_comment(topic=self.topic)
        comment_flag = CommentFlag.objects.create(comment=comment)
        Flag.objects.create(comment=comment, user=user2, reason=0)
        flag_ = Flag.objects.create(comment=comment, user=self.user, reason=0)

        utils.login(self)
        response = self.client.get(reverse('spirit:admin:flag:detail', kwargs={'pk': comment_flag.pk, }))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['flags']), [flag_, ])


class AdminFormTest(TestCase):

    def setUp(self):
        utils.cache_clear()
        self.user = utils.create_user()
        self.category = utils.create_category()
        self.topic = utils.create_topic(self.category)

    def test_user_edit(self):
        """
        Edit user profile
        """
        form_data = {"username": "fooedit",
                     "email": "foo@bar.com",
                     "location": "Bs As",
                     "timezone": "UTC",
                     "is_administrator": True,
                     "is_moderator": True,
                     "is_active": True}
        form = UserForm(data=form_data)
        self.assertEqual(form.is_valid(), True)

        form = UserProfileForm(data=form_data)
        self.assertEqual(form.is_valid(), True)

    def test_basic_config(self):
        """
        basic conf edition
        """
        form_data = {"site_name": "foo",
                     "site_description": "",
                     "template_footer": "",
                     "comments_per_page": 10,
                     "topics_per_page": 10}
        form = BasicConfigForm(data=form_data)
        self.assertEqual(form.is_valid(), True)

        form_data = {"site_name": "foo",
                     "site_description": "bar",
                     "template_footer": "foobar",
                     "comments_per_page": 10,
                     "topics_per_page": 10}
        form = BasicConfigForm(data=form_data)
        self.assertEqual(form.is_valid(), True)

    def test_flag(self):
        """
        flag
        """
        comment = utils.create_comment(topic=self.topic)
        comment_flag = CommentFlag.objects.create(comment=comment)

        form_data = {"is_closed": True, }
        form = CommentFlagForm(user=self.user, data=form_data, instance=comment_flag)
        self.assertEqual(form.is_valid(), True)
        self.assertEqual(form.save().moderator, self.user)
