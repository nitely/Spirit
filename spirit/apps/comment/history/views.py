# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from djconfig import config

from spirit.utils.paginator import yt_paginate
from .models import CommentHistory
from ..models import Comment


@login_required
def detail(request, comment_id):
    comment = get_object_or_404(Comment.objects.for_access(request.user),
                                pk=comment_id)

    comments = CommentHistory.objects\
        .filter(comment_fk=comment)\
        .select_related('comment_fk__user__st')\
        .order_by('date', 'pk')

    comments = yt_paginate(
        comments,
        per_page=config.comments_per_page,
        page_number=request.GET.get('page', 1)
    )

    context = {'comments': comments, }

    return render(request, 'spirit/comment/history/detail.html', context)
