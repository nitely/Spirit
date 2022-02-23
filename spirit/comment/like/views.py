# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from spirit.core.utils.http import safe_redirect
from spirit.core.utils.views import is_post, post_data, is_ajax
from spirit.core.utils import json_response
from spirit.comment.models import Comment
from .models import CommentLike
from .forms import LikeForm


@login_required
def create(request, comment_id):
    comment = get_object_or_404(
        Comment.objects.exclude(user=request.user),
        pk=comment_id)
    form = LikeForm(
        user=request.user,
        comment=comment,
        data=post_data(request))

    if is_post(request) and form.is_valid():
        like = form.save()
        like.comment.increase_likes_count()

        if is_ajax(request):
            return json_response({'url_delete': like.get_delete_url()})

        return safe_redirect(request, 'next', comment.get_absolute_url(), method='POST')

    return render(
        request=request,
        template_name='spirit/comment/like/create.html',
        context={
            'form': form,
            'comment': comment})


@login_required
def delete(request, pk):
    like = get_object_or_404(CommentLike, pk=pk, user=request.user)

    if is_post(request):
        like.delete()
        like.comment.decrease_likes_count()

        if is_ajax(request):
            url = reverse(
                'spirit:comment:like:create',
                kwargs={'comment_id': like.comment.pk})
            return json_response({'url_create': url, })

        return safe_redirect(
            request, 'next', like.comment.get_absolute_url(), method='POST')

    return render(
        request=request,
        template_name='spirit/comment/like/delete.html',
        context={'like': like})
