# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from ...core.utils.views import is_post, post_data
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
        return redirect(request.POST.get('next', comment.get_absolute_url()))

    return render(
        request=request,
        template_name='spirit/comment/flag/create.html',
        context={
            'form': form,
            'comment': comment})
