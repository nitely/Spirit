# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse

from spirit.models.comment import Comment

from spirit.models.comment_like import CommentLike
from spirit.forms.comment_like import LikeForm
from ..signals.comment_like import comment_like_post_create, comment_like_post_delete
from spirit.utils import json_response


@login_required
def like_create(request, comment_id):
    comment = get_object_or_404(Comment.objects.exclude(user=request.user), pk=comment_id)

    if request.method == 'POST':
        form = LikeForm(user=request.user, comment=comment, data=request.POST)

        if form.is_valid():
            like = form.save()
            comment_like_post_create.send(sender=like.__class__, comment=like.comment)

            if request.is_ajax():
                return json_response({'url_delete': like.get_delete_url(), })

            return redirect(request.POST.get('next', comment.get_absolute_url()))
    else:
        form = LikeForm()

    context = {
        'form': form,
        'comment': comment
    }

    return render(request, 'spirit/comment_like/like_create.html', context)


@login_required
def like_delete(request, pk):
    like = get_object_or_404(CommentLike, pk=pk, user=request.user)

    if request.method == 'POST':
        like.delete()
        comment_like_post_delete.send(sender=like.__class__, comment=like.comment)

        if request.is_ajax():
            url = reverse('spirit:like-create', kwargs={'comment_id': like.comment.pk, })
            return json_response({'url_create': url, })

        return redirect(request.POST.get('next', like.comment.get_absolute_url()))

    context = {'like': like, }

    return render(request, 'spirit/comment_like/like_delete.html', context)
