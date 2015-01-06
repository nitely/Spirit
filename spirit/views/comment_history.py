# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

from ..utils.paginator import paginate
from ..models.comment_history import CommentHistory
from ..models.comment import Comment


@login_required
def comment_history_detail(request, comment_id):
    comment = get_object_or_404(Comment.objects.for_access(request.user),
                                pk=comment_id)
    comments = CommentHistory.objects.filter(comment_fk=comment).order_by('date')
    # TODO: paginate
    #comments = paginate(comments, page_num=request.GET.get('page', 1))

    context = {'comments': comments, }

    return render(request, 'spirit/comment_history/detail.html', context)
