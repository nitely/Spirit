#-*- coding: utf-8 -*-

from django.shortcuts import render
from django.contrib.auth import get_user_model

from spirit.utils.decorators import administrator_required

import spirit
from spirit.models.category import Category
from spirit.models.topic import Topic
from spirit.models.comment import Comment
from spirit.models.comment_flag import CommentFlag
from spirit.models.comment_like import CommentLike


User = get_user_model()


@administrator_required
def dashboard(request):
    # Strongly unaccurate counters below...
    category_count = Category.objects.all().count() - 1  # - private
    topics_count = Topic.objects.all().count()
    comments_count = Comment.objects.all().count()
    users_count = User.objects.all().count()
    flags_count = CommentFlag.objects.filter(is_closed=False).count()
    likes_count = CommentLike.objects.all().count()

    return render(request, 'spirit/admin/index/dashboard.html', {'version': spirit.__version__,
                                                                 'category_count': category_count,
                                                                 'topics_count': topics_count,
                                                                 'comments_count': comments_count,
                                                                 'users_count': users_count,
                                                                 'flags_count': flags_count,
                                                                 'likes_count': likes_count})