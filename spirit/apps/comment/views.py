# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import Http404
from djconfig import config

from spirit.utils.ratelimit.decorators import ratelimit
from spirit.utils.decorators import moderator_required
from spirit.utils import json_response, render_form_errors, paginator, markdown
from ..topic.models import Topic
from .models import Comment
from .forms import CommentForm, CommentMoveForm, CommentImageForm
from .signals import comment_posted, comment_pre_update, comment_post_update, comment_moved


@login_required
@ratelimit(rate='1/10s')
def publish(request, topic_id, pk=None):
    topic = get_object_or_404(Topic.objects.opened().for_access(request.user),
                              pk=topic_id)

    if request.method == 'POST':
        form = CommentForm(user=request.user, topic=topic, data=request.POST)

        if not request.is_limited and form.is_valid():
            comment = form.save()
            comment_posted.send(sender=comment.__class__, comment=comment, mentions=form.mentions)
            return redirect(request.POST.get('next', comment.get_absolute_url()))
    else:
        initial = None

        if pk:
            comment = get_object_or_404(Comment.objects.for_access(user=request.user), pk=pk)
            quote = markdown.quotify(comment.comment, comment.user.username)
            initial = {'comment': quote, }

        form = CommentForm(initial=initial)

    context = {
        'form': form,
        'topic': topic
    }

    return render(request, 'spirit/comment/publish.html', context)


@login_required
def update(request, pk):
    comment = Comment.objects.for_update_or_404(pk, request.user)

    if request.method == 'POST':
        form = CommentForm(data=request.POST, instance=comment)

        if form.is_valid():
            comment_pre_update.send(sender=comment.__class__, comment=Comment.objects.get(pk=comment.pk))
            comment = form.save()
            comment_post_update.send(sender=comment.__class__, comment=comment)
            return redirect(request.POST.get('next', comment.get_absolute_url()))
    else:
        form = CommentForm(instance=comment)

    context = {'form': form, }

    return render(request, 'spirit/comment/update.html', context)


@moderator_required
def delete(request, pk, remove=True):
    comment = get_object_or_404(Comment, pk=pk)

    if request.method == 'POST':
        Comment.objects.filter(pk=pk)\
            .update(is_removed=remove)

        return redirect(comment.get_absolute_url())

    context = {'comment': comment, }

    return render(request, 'spirit/comment/moderate.html', context)


@require_POST
@moderator_required
def move(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)
    form = CommentMoveForm(topic=topic, data=request.POST)

    if form.is_valid():
        comments = form.save()

        for comment in comments:
            comment_posted.send(sender=comment.__class__, comment=comment, mentions=None)

        comment_moved.send(sender=Comment, comments=comments, topic_from=topic)
    else:
        messages.error(request, render_form_errors(form))

    return redirect(request.POST.get('next', topic.get_absolute_url()))


def find(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment_number = Comment.objects.filter(topic=comment.topic, date__lte=comment.date).count()
    url = paginator.get_url(comment.topic.get_absolute_url(),
                            comment_number,
                            config.comments_per_page,
                            'page')
    return redirect(url)


@require_POST
@login_required
def image_upload_ajax(request):
    if not request.is_ajax():
        return Http404()

    form = CommentImageForm(user=request.user, data=request.POST, files=request.FILES)

    if form.is_valid():
        image = form.save()
        return json_response({'url': image.url, })

    return json_response({'error': dict(form.errors.items()), })
