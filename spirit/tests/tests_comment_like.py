#-*- coding: utf-8 -*-

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.template import Template, Context, TemplateSyntaxError
from django.core.cache import cache

import utils

from spirit.models.comment_like import CommentLike
from spirit.forms.comment_like import LikeForm
from spirit.templatetags.tags.comment_like import render_like_form


class LikeViewTest(TestCase):

    fixtures = ['spirit_init.json', ]

    def setUp(self):
        cache.clear()
        self.user = utils.create_user()
        self.category = utils.create_category()
        self.topic = utils.create_topic(category=self.category, user=self.user)
        self.comment = utils.create_comment(topic=self.topic)

    def test_like_create(self):
        """
        create like
        """
        utils.login(self)
        form_data = {}
        response = self.client.post(reverse('spirit:like-create', kwargs={'comment_id': self.comment.pk, }),
                                    form_data)
        self.assertRedirects(response, self.comment.get_absolute_url(), status_code=302, target_status_code=302)
        self.assertEqual(len(CommentLike.objects.all()), 1)

    def test_like_create_next(self):
        """
        create like using next
        """
        utils.login(self)
        form_data = {'next': '/fakepath/', }
        response = self.client.post(reverse('spirit:like-create', kwargs={'comment_id': self.comment.pk, }),
                                    form_data)
        self.assertRedirects(response, '/fakepath/', status_code=302, target_status_code=404)

    def test_like_create_invalid(self):
        """
        create like invalid
        """
        CommentLike.objects.create(user=self.user, comment=self.comment)
        utils.login(self)
        form_data = {}
        response = self.client.post(reverse('spirit:like-create', kwargs={'comment_id': self.comment.pk, }),
                                    form_data)
        self.assertEqual(response.status_code, 200)

    def test_like_delete(self):
        """
        delete like
        """
        utils.login(self)
        like = CommentLike.objects.create(user=self.user, comment=self.comment)
        form_data = {}
        response = self.client.post(reverse('spirit:like-delete', kwargs={'pk': like.pk, }),
                                    form_data)
        self.assertRedirects(response, self.comment.get_absolute_url(), status_code=302, target_status_code=302)
        self.assertEqual(len(CommentLike.objects.all()), 0)

    def test_like_delete_next(self):
        """
        delete like using next
        """
        utils.login(self)
        like = CommentLike.objects.create(user=self.user, comment=self.comment)
        form_data = {'next': '/fakepath/', }
        response = self.client.post(reverse('spirit:like-delete', kwargs={'pk': like.pk, }),
                                    form_data)
        self.assertRedirects(response, '/fakepath/', status_code=302, target_status_code=404)


class LikeFormTest(TestCase):

    fixtures = ['spirit_init.json', ]

    def setUp(self):
        cache.clear()
        self.user = utils.create_user()
        self.category = utils.create_category()
        self.topic = utils.create_topic(category=self.category, user=self.user)
        self.comment = utils.create_comment(user=self.user, topic=self.topic)

    def test_like_create(self):
        """
        create like
        """
        form_data = {}
        form = LikeForm(data=form_data)
        form.comment = self.comment
        form.user = self.user
        self.assertEqual(form.is_valid(), True)

    def test_like_create_invalid(self):
        """
        create like twice
        """
        CommentLike.objects.create(user=self.user, comment=self.comment)
        form_data = {}
        form = LikeForm(data=form_data)
        form.comment = self.comment
        form.user = self.user
        self.assertEqual(form.is_valid(), False)


class LikeTemplateTagsTest(TestCase):

    fixtures = ['spirit_init.json', ]

    def setUp(self):
        cache.clear()
        self.user = utils.create_user()
        self.category = utils.create_category()
        self.topic = utils.create_topic(category=self.category, user=self.user)
        self.comment = utils.create_comment(topic=self.topic)

    def test_like_render_like_form(self):
        """
        should display the like form
        """
        template = Template(
            "{% load spirit_tags %}"
            "{% render_like_form comment=comment like=like %}"
        )
        data = {'comment': self.comment, 'like': None}
        out = template.render(Context(data))
        context = render_like_form(**data)
        self.assertEqual(context['next'], None)
        self.assertIsInstance(context['form'], LikeForm)
        self.assertEqual(context['comment_id'], self.comment.pk)
        self.assertEqual(context['like'], None)

        like = CommentLike.objects.create(user=self.user, comment=self.comment)
        data['like'] = like
        out = template.render(Context(data))
        context = render_like_form(**data)
        self.assertEqual(context['like'], like)

    def test_like_populate_likes(self):
        """
        should populate comments likes, tell if current user liked the comment
        """
        like = CommentLike.objects.create(user=self.user, comment=self.comment)
        out = Template(
            "{% load spirit_tags %}"
            "{% populate_likes comments=comments user=user %}"
            "{{ comments.0.like }}"
        ).render(Context({'comments': [self.comment, ], 'user': self.user}))
        self.assertEqual(out, str(like))