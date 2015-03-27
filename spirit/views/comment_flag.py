# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from spirit.models.comment import Comment

from spirit.forms.comment_flag import FlagForm


@login_required
def flag_create(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)

    if request.method == 'POST':
        form = FlagForm(user=request.user, comment=comment, data=request.POST)

        if form.is_valid():
            form.save()
            return redirect(request.POST.get('next', comment.get_absolute_url()))
    else:
        form = FlagForm()

    context = {
        'form': form,
        'comment': comment
    }

    return render(request, 'spirit/comment_flag/flag_create.html', context)
