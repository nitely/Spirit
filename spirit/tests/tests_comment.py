#-*- coding: utf-8 -*-

import time

from django.test import TestCase, RequestFactory
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.template import Template, Context, TemplateSyntaxError
from django.test.signals import template_rendered
from django.utils.translation import ugettext as _
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User as UserModel
from django.contrib.auth import get_user_model

import utils

from spirit.models.comment import Comment,\
    comment_like_post_create, comment_like_post_delete,\
    topic_post_moderate, comment_post_update
from spirit.forms.comment import CommentForm, CommentMoveForm
from spirit.signals.comment import comment_post_update, comment_posted, comment_pre_update
from spirit.templatetags.tags.comment import render_comments_form
from spirit.utils import markdown
from spirit.views.comment import comment_delete
from spirit.models.topic import Topic


User = get_user_model()


class CommentViewTest(TestCase):

    fixtures = ['spirit_init.json', ]

    def setUp(self):
        cache.clear()
        self.user = utils.create_user()
        self.category = utils.create_category()
        self.topic = utils.create_topic(category=self.category, user=self.user)

    def test_comment_publish(self):
        """
        create comment
        """
        utils.login(self)
        form_data = {'comment': 'foobar', }
        response = self.client.post(reverse('spirit:comment-publish', kwargs={'topic_id': self.topic.pk, }),
                                    form_data)
        expected_url = reverse('spirit:comment-find', kwargs={'pk': 1, })
        self.assertRedirects(response, expected_url, status_code=302, target_status_code=302)
        self.assertEqual(len(Comment.objects.all()), 1)

        # ratelimit
        response = self.client.post(reverse('spirit:comment-publish', kwargs={'topic_id': self.topic.pk, }),
                                    form_data)
        self.assertEqual(len(Comment.objects.all()), 1)

        # get
        response = self.client.get(reverse('spirit:comment-publish', kwargs={'topic_id': self.topic.pk, }))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['topic'], self.topic)

    def test_comment_publish_on_private(self):
        """
        create comment on private topic
        """
        private = utils.create_private_topic(user=self.user)

        utils.login(self)
        form_data = {'comment': 'foobar', }
        response = self.client.post(reverse('spirit:comment-publish', kwargs={'topic_id': private.topic.pk, }),
                                    form_data)
        expected_url = reverse('spirit:comment-find', kwargs={'pk': 1, })
        self.assertRedirects(response, expected_url, status_code=302, target_status_code=302)
        self.assertEqual(len(Comment.objects.all()), 1)

    def test_comment_publish_on_closed_topic(self):
        """
        should not be able to create a comment on a closed topic
        """
        Topic.objects.filter(pk=self.topic.pk).update(is_closed=True)

        utils.login(self)
        form_data = {'comment': 'foobar', }
        response = self.client.post(reverse('spirit:comment-publish', kwargs={'topic_id': self.topic.pk, }),
                                    form_data)
        self.assertEqual(response.status_code, 404)

    def test_comment_publish_no_access(self):
        """
        should not be able to create a comment on a private topic if has no access
        """
        private = utils.create_private_topic(user=self.user)
        private.delete()

        utils.login(self)
        form_data = {'comment': 'foobar', }
        response = self.client.post(reverse('spirit:comment-publish', kwargs={'topic_id': private.topic.pk, }),
                                    form_data)
        self.assertEqual(response.status_code, 404)

    def test_comment_publish_signal(self):
        """
        create comment signal
        """
        def comment_posted_handler(sender, comment, **kwargs):
            self._comment = comment
        comment_posted.connect(comment_posted_handler)

        utils.login(self)
        form_data = {'comment': 'foobar', }
        response = self.client.post(reverse('spirit:comment-publish', kwargs={'topic_id': self.topic.pk, }),
                                    form_data)
        self.assertEqual(self._comment.comment, 'foobar')

    def test_comment_publish_quote(self):
        """
        create comment quote
        """
        utils.login(self)
        comment = utils.create_comment(topic=self.topic)
        response = self.client.get(reverse('spirit:comment-publish', kwargs={'topic_id': self.topic.pk,
                                                                             'pk': comment.pk}))
        self.assertEqual(response.context['form'].initial['comment'],
                         markdown.quotify(comment.comment, comment.user.username))

    def test_comment_publish_next(self):
        """
        next on create comment
        """
        utils.login(self)
        form_data = {'comment': 'foobar', 'next': '/fakepath/'}
        response = self.client.post(reverse('spirit:comment-publish', kwargs={'topic_id': self.topic.pk, }),
                                    form_data)
        self.assertRedirects(response, '/fakepath/', status_code=302, target_status_code=404)

    def test_comment_update(self):
        """
        update comment
        """
        comment = utils.create_comment(user=self.user, topic=self.topic)

        utils.login(self)
        form_data = {'comment': 'barfoo', }
        response = self.client.post(reverse('spirit:comment-update', kwargs={'pk': comment.pk, }),
                                    form_data)
        expected_url = reverse('spirit:comment-find', kwargs={'pk': 1, })
        self.assertRedirects(response, expected_url, status_code=302, target_status_code=302)
        self.assertEqual(Comment.objects.get(pk=comment.pk).comment, 'barfoo')

        # next
        form_data.update({'next': '/fakepath/', })
        response = self.client.post(reverse('spirit:comment-update', kwargs={'pk': comment.pk, }),
                                    form_data)
        self.assertRedirects(response, '/fakepath/', status_code=302, target_status_code=404)

    def test_comment_update_not_moderator(self):
        """
        non moderators can not update other people comments
        """
        user = utils.create_user()
        comment = utils.create_comment(user=user, topic=self.topic)

        utils.login(self)
        form_data = {'comment': 'barfoo', }
        response = self.client.post(reverse('spirit:comment-update', kwargs={'pk': comment.pk, }),
                                    form_data)
        self.assertEqual(response.status_code, 404)

    def test_comment_update_moderator(self):
        """
        moderators can update other people comments
        """
        User.objects.filter(pk=self.user.pk).update(is_moderator=True)
        user = utils.create_user()
        comment = utils.create_comment(user=user, topic=self.topic)

        utils.login(self)
        form_data = {'comment': 'barfoo', }
        response = self.client.post(reverse('spirit:comment-update', kwargs={'pk': comment.pk, }),
                                    form_data)
        expected_url = reverse('spirit:comment-find', kwargs={'pk': 1, })
        self.assertRedirects(response, expected_url, status_code=302, target_status_code=302)
        self.assertEqual(Comment.objects.get(pk=comment.pk).comment, 'barfoo')

    def test_comment_update_signal(self):
        """
        update comment, emit signal
        """
        def comment_pre_update_handler(sender, comment, **kwargs):
            self._comment_old = comment
        comment_pre_update.connect(comment_pre_update_handler)

        def comment_post_update_handler(sender, comment, **kwargs):
            self._comment_new = comment
        comment_post_update.connect(comment_post_update_handler)

        utils.login(self)
        comment_posted = utils.create_comment(user=self.user, topic=self.topic)
        form_data = {'comment': 'barfoo', }
        response = self.client.post(reverse('spirit:comment-update', kwargs={'pk': comment_posted.pk, }),
                                    form_data)
        self.assertEqual(repr(self._comment_new), repr(Comment.objects.get(pk=comment_posted.pk)))
        self.assertEqual(repr(self._comment_old), repr(comment_posted))

    def test_comment_delete_permission_denied_to_non_moderator(self):
        req = RequestFactory().get('/')
        req.user = UserModel()
        req.user.is_moderator = False
        self.assertRaises(PermissionDenied, comment_delete, req)

    def test_comment_delete(self):
        """
        comment delete
        """
        self.user = utils.create_user(is_moderator=True)
        comment = utils.create_comment(user=self.user, topic=self.topic)

        utils.login(self)
        form_data = {}
        response = self.client.post(reverse('spirit:comment-delete', kwargs={'pk': comment.pk, }),
                                    form_data)
        expected_url = comment.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302, target_status_code=302)

        response = self.client.get(reverse('spirit:comment-delete', kwargs={'pk': comment.pk, }))
        self.assertEqual(response.status_code, 200)

    def test_comment_undelete(self):
        """
        comment undelete
        """
        self.user = utils.create_user(is_moderator=True)
        comment = utils.create_comment(user=self.user, topic=self.topic, is_removed=True)

        utils.login(self)
        form_data = {}
        response = self.client.post(reverse('spirit:comment-undelete', kwargs={'pk': comment.pk, }),
                                    form_data)
        expected_url = comment.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302, target_status_code=302)

        response = self.client.get(reverse('spirit:comment-undelete', kwargs={'pk': comment.pk, }))
        self.assertEqual(response.status_code, 200)

    def test_comment_move(self):
        """
        comment move to another topic
        """
        utils.login(self)
        self.user.is_moderator = True
        self.user.save()
        comment = utils.create_comment(user=self.user, topic=self.topic)
        comment2 = utils.create_comment(user=self.user, topic=self.topic)
        to_topic = utils.create_topic(category=self.category)
        form_data = {'topic': to_topic.pk,
                     'comments': [comment.pk, comment2.pk], }
        response = self.client.post(reverse('spirit:comment-move', kwargs={'topic_id': self.topic.pk, }),
                                    form_data)
        expected_url = self.topic.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302)
        self.assertEqual(Comment.objects.filter(topic=to_topic.pk).count(), 2)
        self.assertEqual(Comment.objects.filter(topic=self.topic.pk).count(), 0)

    def test_comment_find(self):
        """
        comment absolute and lazy url
        """
        comment = utils.create_comment(user=self.user, topic=self.topic)
        response = self.client.post(reverse('spirit:comment-find', kwargs={'pk': comment.pk, }))
        expected_url = comment.topic.get_absolute_url() + "#c%d" % comment.pk
        self.assertRedirects(response, expected_url, status_code=302)


class CommentSignalTest(TestCase):

    fixtures = ['spirit_init.json', ]

    def setUp(self):
        cache.clear()
        self.user = utils.create_user()
        self.category = utils.create_category()
        self.topic = utils.create_topic(category=self.category, user=self.user)

    def test_comment_comment_post_update_handler(self):
        """
        Increase modified_count on updated comment
        """
        comment = utils.create_comment(topic=self.topic)
        comment_post_update.send(sender=comment.__class__, comment=comment)
        self.assertEqual(Comment.objects.get(pk=comment.pk).modified_count, 1)

    def test_comment_comment_like_post_create_handler(self):
        """
        Increase like_count on comment like
        """
        comment = utils.create_comment(topic=self.topic)
        comment_like_post_create.send(sender=comment.__class__, comment=comment)
        self.assertEqual(Comment.objects.get(pk=comment.pk).likes_count, 1)

    def test_comment_comment_like_post_delete_handler(self):
        """
        Decrease like_count on remove comment like
        """
        comment = utils.create_comment(topic=self.topic)
        comment_like_post_create.send(sender=comment.__class__, comment=comment)
        self.assertEqual(Comment.objects.get(pk=comment.pk).likes_count, 1)
        comment_like_post_delete.send(sender=comment.__class__, comment=comment)
        self.assertEqual(Comment.objects.get(pk=comment.pk).likes_count, 0)

    def test_topic_post_moderate_handler(self):
        """
        Create comment that tells what moderation action was made
        """
        topic_post_moderate.send(sender=None, user=self.user, topic=self.topic, action=1)
        self.assertEqual(Comment.objects.filter(user=self.user, topic=self.topic, action=1).count(), 1)


class CommentTemplateTagTests(TestCase):

    fixtures = ['spirit_init.json', ]

    def setUp(self):
        cache.clear()
        self.user = utils.create_user()
        self.category = utils.create_category()
        self.topic = utils.create_topic(category=self.category, user=self.user)
        utils.create_comment(topic=self.topic)
        utils.create_comment(topic=self.topic)
        utils.create_comment(topic=self.topic)

    def test_get_comment_list(self):
        """
        should display all comment for a topic
        """
        out = Template(
            "{% load spirit_tags %}"
            "{% get_comment_list topic as comments %}"
            "{% for c in comments %}"
            "{{ c.comment }},"
            "{% endfor %}"
        ).render(Context({'topic': self.topic, }))
        self.assertEqual(out, "foobar0,foobar1,foobar2,")

    def test_render_comments_form(self):
        """
        should display simple comment form
        """
        out = Template(
            "{% load spirit_tags %}"
            "{% render_comments_form topic %}"
        ).render(Context({'topic': self.topic, }))
        context = render_comments_form(self.topic)
        self.assertEqual(context['next'], None)
        self.assertIsInstance(context['form'], CommentForm)
        self.assertEqual(context['topic_id'], self.topic.pk)

    def test_get_action_text(self):
        """
        should display action
        """
        out = Template(
            "{% load spirit_tags %}"
            "{% get_comment_action_text 1 %}"
        ).render(Context())
        self.assertNotEqual(out, "")


class CommentFormTest(TestCase):

    fixtures = ['spirit_init.json', ]

    def setUp(self):
        cache.clear()
        self.user = utils.create_user()
        self.category = utils.create_category()
        self.topic = utils.create_topic(category=self.category)

    def test_comment_create(self):
        form_data = {'comment': 'foo', }
        form = CommentForm(data=form_data)
        self.assertEqual(form.is_valid(), True)

    def test_comment_markdown(self):
        form_data = {'comment': u'**Spirit unicode: áéíóú** '
                                u'<script>alert();</script>', }
        form = CommentForm(data=form_data)
        self.assertEqual(form.is_valid(), True)
        form.user = self.user
        form.topic = self.topic
        comment = form.save()
        self.assertEqual(comment.comment_html, u'<p><strong>Spirit unicode: áéíóú</strong> '
                                               u'&lt;script&gt;alert();&lt;/script&gt;</p>')

    def test_comments_move(self):
        comment = utils.create_comment(user=self.user, topic=self.topic)
        comment2 = utils.create_comment(user=self.user, topic=self.topic)
        to_topic = utils.create_topic(category=self.category)
        form_data = {'topic': to_topic.pk,
                     'comments': [comment.pk, comment2.pk], }
        form = CommentMoveForm(topic=self.topic, data=form_data)
        self.assertEqual(form.is_valid(), True)
        self.assertEqual(form.save(), list(Comment.objects.filter(topic=to_topic)))