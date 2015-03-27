# -*- coding: utf-8 -*-

from __future__ import unicode_literals

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
    context = {
        'version': spirit.__version__,
        'category_count': Category.objects.all().count() - 1,  # - private
        'topics_count': Topic.objects.all().count(),
        'comments_count': Comment.objects.all().count(),
        'users_count': User.objects.all().count(),
        'flags_count': CommentFlag.objects.filter(is_closed=False).count(),
        'likes_count': CommentLike.objects.all().count()
    }

    return render(request, 'spirit/admin/index/dashboard.html', context)
