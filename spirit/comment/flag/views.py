# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

from spirit.core.utils.http import safe_redirect
from spirit.core.utils.views import is_post, post_data
from ..models import Comment
from .forms import FlagForm


@login_required
def create(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    form = FlagForm(
        user=request.user,
        comment=comment,
        data=post_data(request))

    if is_post(request) and form.is_valid():
        form.save()
        return safe_redirect(request, 'next', comment.get_absolute_url(), method='POST')

    return render(
        request=request,
        template_name='spirit/comment/flag/create.html',
        context={
            'form': form,
            'comment': comment})
