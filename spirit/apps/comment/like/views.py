# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse

from spirit.utils import json_response
from ..models import Comment
from .models import CommentLike
from .forms import LikeForm
from .signals import comment_like_post_create, comment_like_post_delete


@login_required
def create(request, comment_id):
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

    return render(request, 'spirit/comment/like/create.html', context)


@login_required
def delete(request, pk):
    like = get_object_or_404(CommentLike, pk=pk, user=request.user)

    if request.method == 'POST':
        like.delete()
        comment_like_post_delete.send(sender=like.__class__, comment=like.comment)

        if request.is_ajax():
            url = reverse('spirit:like-create', kwargs={'comment_id': like.comment.pk, })
            return json_response({'url_create': url, })

        return redirect(request.POST.get('next', like.comment.get_absolute_url()))

    context = {'like': like, }

    return render(request, 'spirit/comment/like/delete.html', context)
