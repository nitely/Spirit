# -*- coding: utf-8 -*-

from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.translation import gettext as _
from django.contrib.auth import get_user_model

import spirit
import django
from spirit.category.models import Category
from spirit.comment.flag.models import CommentFlag
from spirit.comment.like.models import CommentLike
from spirit.comment.models import Comment
from spirit.topic.models import Topic
from spirit.core.utils.views import is_post, post_data
from spirit.core.utils.decorators import administrator_required
from .forms import BasicConfigForm

User = get_user_model()


@administrator_required
def config_basic(request):
    form = BasicConfigForm(data=post_data(request))
    if is_post(request) and form.is_valid():
        form.save()
        messages.info(request, _("Settings updated!"))
        return redirect(request.GET.get("next", request.get_full_path()))
    return render(
        request=request,
        template_name='spirit/admin/config_basic.html',
        context={'form': form})


@administrator_required
def dashboard(request):
    # Strongly inaccurate counters below...
    context = {
        'version': spirit.__version__,
        'django_version': django.get_version(),
        'category_count': Category.objects.all().count() - 1,  # - private
        'topics_count': Topic.objects.all().count(),
        'comments_count': Comment.objects.all().count(),
        'users_count': User.objects.all().count(),
        'flags_count': CommentFlag.objects.filter(is_closed=False).count(),
        'likes_count': CommentLike.objects.all().count()
    }

    return render(request, 'spirit/admin/dashboard.html', context)
