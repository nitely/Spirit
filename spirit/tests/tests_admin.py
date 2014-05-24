#-*- coding: utf-8 -*-

from django.test import TestCase, RequestFactory
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User as UserModel
from django.contrib.auth import get_user_model

import utils

from spirit.views.admin import user, category, comment_flag, config, index, topic
from spirit.models.category import Category
from spirit.models.comment_flag import CommentFlag, Flag
from spirit.forms.admin import UserEditForm, CategoryForm, BasicConfigForm, CommentFlagForm


User = get_user_model()


class AdminViewTest(TestCase):

    fixtures = ['spirit_init.json', ]

    def setUp(self):
        cache.clear()
        self.user = utils.create_user(is_administrator=True)
        self.category = utils.create_category()
        self.topic = utils.create_topic(self.category, user=self.user)

    def test_permission_denied_to_non_admin(self):
        req = RequestFactory().get('/')
        req.user = UserModel()
        req.user.is_administrator = False

        self.assertRaises(PermissionDenied, category.category_list, req)
        self.assertRaises(PermissionDenied, category.category_create, req)
        self.assertRaises(PermissionDenied, category.category_update, req)

        self.assertRaises(PermissionDenied, comment_flag.flag_closed, req)
        self.assertRaises(PermissionDenied, comment_flag.flag_open, req)
        self.assertRaises(PermissionDenied, comment_flag.flag_detail, req)

        self.assertRaises(PermissionDenied, config.config_basic, req)

        self.assertRaises(PermissionDenied, index.dashboard, req)

        self.assertRaises(PermissionDenied, topic.topic_deleted, req)
        self.assertRaises(PermissionDenied, topic.topic_closed, req)
        self.assertRaises(PermissionDenied, topic.topic_pinned, req)

        self.assertRaises(PermissionDenied, user.user_edit, req)
        self.assertRaises(PermissionDenied, user.user_list, req)
        self.assertRaises(PermissionDenied, user.user_admins, req)
        self.assertRaises(PermissionDenied, user.user_mods, req)
        self.assertRaises(PermissionDenied, user.user_unactive, req)

    def test_user_edit(self):
        """
        Edit user profile
        """
        utils.login(self)
        form_data = {"username": "fooedit", "email": "foo@bar.com", "location": "Bs As",
                     "timezone": "UTC", "is_administrator": True, "is_moderator": True, "is_active": True}
        response = self.client.post(reverse('spirit:admin-user-edit', kwargs={'user_id': self.user.pk, }),
                                    form_data)
        expected_url = reverse('spirit:admin-user-edit', kwargs={'user_id': self.user.pk, })
        self.assertRedirects(response, expected_url, status_code=302)

        response = self.client.get(reverse('spirit:admin-user-edit', kwargs={'user_id': self.user.pk, }))
        self.assertEqual(response.status_code, 200)

    def test_user_list(self):
        """
        List of all users
        """
        utils.login(self)
        response = self.client.get(reverse('spirit:admin-user-list'))
        self.assertQuerysetEqual(response.context['users'], map(repr, [self.user, ]))

    def test_user_admins(self):
        """
        List of admins
        """
        utils.login(self)
        response = self.client.get(reverse('spirit:admin-user-admins'))
        self.assertQuerysetEqual(response.context['users'], map(repr, [self.user, ]))

    def test_user_mods(self):
        """
        List of admins
        """
        mod = utils.create_user(is_moderator=True)
        utils.login(self)
        response = self.client.get(reverse('spirit:admin-user-mods'))
        self.assertQuerysetEqual(response.context['users'], map(repr, [mod, ]))

    def test_user_unactive(self):
        """
        List of unactive
        """
        unactive = utils.create_user()
        User.objects.filter(pk=unactive.pk).update(is_active=False)
        utils.login(self)
        response = self.client.get(reverse('spirit:admin-user-unactive'))
        self.assertQuerysetEqual(response.context['users'], map(repr, [unactive, ]))

    def test_index_dashboard(self):
        utils.login(self)
        response = self.client.get(reverse('spirit:admin-topic'))
        self.assertEqual(response.status_code, 200)

    def test_topic_deleted(self):
        """
        Deleted topics
        """
        topic_ = utils.create_topic(self.category, is_removed=True)
        utils.login(self)
        response = self.client.get(reverse('spirit:admin-topic-deleted'))
        self.assertQuerysetEqual(response.context['topics'], map(repr, [topic_, ]))

    def test_topic_closed(self):
        """
        Closed topics
        """
        topic_ = utils.create_topic(self.category, is_closed=True)
        utils.login(self)
        response = self.client.get(reverse('spirit:admin-topic-closed'))
        self.assertQuerysetEqual(response.context['topics'], map(repr, [topic_, ]))

    def test_topic_pinned(self):
        """
        Pinned topics
        """
        topic_ = utils.create_topic(self.category, is_pinned=True)
        utils.login(self)
        response = self.client.get(reverse('spirit:admin-topic-pinned'))
        self.assertQuerysetEqual(response.context['topics'], map(repr, [topic_, ]))

    def test_category_list(self):
        """
        Categories, excludes Topic Private and subcats
        """
        subcat = utils.create_category(parent=self.category)
        categories = Category.objects.filter(is_private=False, parent=None)
        utils.login(self)
        response = self.client.get(reverse('spirit:admin-category-list'))
        self.assertQuerysetEqual(response.context['categories'], map(repr, categories))

    def test_category_create(self):
        """
        Category create
        """
        utils.login(self)
        form_data = {"parent": "", "title": "foo", "description": "", "is_closed": False, "is_removed": False}
        response = self.client.post(reverse('spirit:admin-category-create'),
                                    form_data)
        expected_url = reverse("spirit:admin-category-list")
        self.assertRedirects(response, expected_url, status_code=302)

        response = self.client.get(reverse('spirit:admin-category-create'))
        self.assertEqual(response.status_code, 200)

    def test_category_update(self):
        """
        Category update
        """
        utils.login(self)
        form_data = {"parent": "", "title": "foo", "description": "", "is_closed": False, "is_removed": False}
        response = self.client.post(reverse('spirit:admin-category-update', kwargs={"category_id": self.category.pk, }),
                                    form_data)
        expected_url = reverse("spirit:admin-category-list")
        self.assertRedirects(response, expected_url, status_code=302)

        response = self.client.get(reverse('spirit:admin-category-update', kwargs={"category_id": self.category.pk, }))
        self.assertEqual(response.status_code, 200)

    def test_config_basic(self):
        """
        Config
        """
        utils.login(self)
        form_data = {"site_name": "foo", "site_description": "bar"}
        response = self.client.post(reverse('spirit:admin-config-basic'),
                                    form_data)
        expected_url = reverse('spirit:admin-config-basic')
        self.assertRedirects(response, expected_url, status_code=302)

        response = self.client.get(reverse('spirit:admin-config-basic'))
        self.assertEqual(response.status_code, 200)

    def test_flag_open(self):
        """
        Open flags
        """
        comment = utils.create_comment(topic=self.topic)
        comment2 = utils.create_comment(topic=self.topic)
        flag_closed = CommentFlag.objects.create(comment=comment2, is_closed=True)
        flag_ = CommentFlag.objects.create(comment=comment)

        utils.login(self)
        response = self.client.get(reverse('spirit:admin-flag-open'))
        self.assertQuerysetEqual(response.context['flags'], map(repr, [flag_, ]))

    def test_flag_closed(self):
        """
        Open flags
        """
        comment = utils.create_comment(topic=self.topic)
        comment2 = utils.create_comment(topic=self.topic)
        flag_closed = CommentFlag.objects.create(comment=comment2, is_closed=True)
        flag_ = CommentFlag.objects.create(comment=comment)

        utils.login(self)
        response = self.client.get(reverse('spirit:admin-flag-closed'))
        self.assertQuerysetEqual(response.context['flags'], map(repr, [flag_closed, ]))

    def test_flag_detail(self):
        """
        flag detail
        """
        comment = utils.create_comment(topic=self.topic)
        comment_flag = CommentFlag.objects.create(comment=comment)
        flag_ = Flag.objects.create(comment=comment, user=self.user, reason=0)

        comment2 = utils.create_comment(topic=self.topic)
        comment_flag2 = CommentFlag.objects.create(comment=comment2)
        flag_2 = Flag.objects.create(comment=comment2, user=self.user, reason=0)

        utils.login(self)
        form_data = {"is_closed": True, }
        response = self.client.post(reverse('spirit:admin-flag-detail', kwargs={'pk': comment_flag.pk, }),
                                    form_data)
        expected_url = reverse('spirit:admin-flag')
        self.assertRedirects(response, expected_url, status_code=302)

        response = self.client.get(reverse('spirit:admin-flag-detail', kwargs={'pk': comment_flag.pk, }))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(repr(response.context['flag']), repr(comment_flag))
        self.assertQuerysetEqual(response.context['flags'], map(repr, [flag_, ]))


class AdminFormTest(TestCase):

    fixtures = ['spirit_init.json', ]

    def setUp(self):
        cache.clear()
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
        form = UserEditForm(data=form_data)
        self.assertEqual(form.is_valid(), True)

    def test_category(self):
        """
        Add category
        """
        form_data = {"parent": "",
                     "title": "foo",
                     "description": "",
                     "is_closed": False,
                     "is_removed": False}
        form = CategoryForm(data=form_data)
        self.assertEqual(form.is_valid(), True)

    def test_category_invalid_parent(self):
        """
        invalid parent
        """
        # parent can not be a subcategory, only one level subcat is allowed
        subcategory = utils.create_category(parent=self.category)
        form_data = {"parent": subcategory.pk, }
        form = CategoryForm(data=form_data)
        self.assertEqual(form.is_valid(), False)
        self.assertNotIn('parent', form.cleaned_data)

        # parent can not be set to a category with childrens
        category_ = utils.create_category()
        form_data = {"parent": category_.pk, }
        form = CategoryForm(data=form_data, instance=self.category)
        self.assertEqual(form.is_valid(), False)
        self.assertNotIn('parent', form.cleaned_data)

        # parent can not be removed
        category_ = utils.create_category(is_removed=True)
        form_data = {"parent": category_.pk, }
        form = CategoryForm(data=form_data)
        self.assertEqual(form.is_valid(), False)
        self.assertNotIn('parent', form.cleaned_data)

        # parent can not be private
        category_ = utils.create_category(is_private=True)
        form_data = {"parent": category_.pk, }
        form = CategoryForm(data=form_data)
        self.assertEqual(form.is_valid(), False)
        self.assertNotIn('parent', form.cleaned_data)

    def test_basic_config(self):
        """
        basic conf edition
        """
        form_data = {"site_name": "foo",
                     "site_description": "",
                     "template_footer": ""}
        form = BasicConfigForm(data=form_data)
        self.assertEqual(form.is_valid(), True)

        form_data = {"site_name": "foo",
                     "site_description": "bar",
                     "template_footer": "foobar"}
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
        self.assertEqual(repr(form.save().moderator), repr(self.user))