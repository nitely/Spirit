# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.contrib.auth import get_user_model

import spirit
from spirit.apps.category.models import Category
from spirit.apps.comment.flag.models import CommentFlag
from spirit.apps.comment.like.models import CommentLike
from spirit.apps.comment.models import Comment
from spirit.apps.topic.models import Topic
from spirit.utils.decorators import administrator_required
from spirit.apps.admin.forms import BasicConfigForm


User = get_user_model()


@administrator_required
def config_basic(request):

    if request.method == 'POST':
        form = BasicConfigForm(data=request.POST)

        if form.is_valid():
            form.save()
            messages.info(request, _("Settings updated!"))
            return redirect(request.GET.get("next", request.get_full_path()))
    else:
        form = BasicConfigForm()

    context = {'form': form, }

    return render(request, 'spirit/admin/config_basic.html', context)


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

    return render(request, 'spirit/admin/dashboard.html', context)