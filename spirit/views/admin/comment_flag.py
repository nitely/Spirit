# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.translation import ugettext as _

from djconfig import config

from ...utils.paginator import yt_paginate
from ...utils.decorators import administrator_required

from ...models.comment_flag import CommentFlag, Flag
from ...forms.admin import CommentFlagForm


@administrator_required
def flag_open(request):
    flags = yt_paginate(
        CommentFlag.objects.filter(is_closed=False),
        per_page=config.comments_per_page,
        page_number=request.GET.get('page', 1)
    )
    context = {'flags': flags, }
    return render(request, 'spirit/admin/comment_flag/flag_open.html', context)


@administrator_required
def flag_closed(request):
    flags = yt_paginate(
        CommentFlag.objects.filter(is_closed=True),
        per_page=config.comments_per_page,
        page_number=request.GET.get('page', 1)
    )
    context = {'flags': flags, }
    return render(request, 'spirit/admin/comment_flag/flag_closed.html', context)


@administrator_required
def flag_detail(request, pk):
    flag = get_object_or_404(CommentFlag, pk=pk)

    if request.method == 'POST':
        form = CommentFlagForm(user=request.user, data=request.POST, instance=flag)

        if form.is_valid():
            form.save()
            messages.info(request, _("The flag has been moderated!"))
            return redirect(reverse("spirit:admin-flag"))
    else:
        form = CommentFlagForm(instance=flag)

    flags = yt_paginate(
        Flag.objects.filter(comment=flag.comment),
        per_page=config.comments_per_page,
        page_number=request.GET.get('page', 1)
    )

    context = {
        'flag': flag,
        'flags': flags,
        'form': form
    }

    return render(request, 'spirit/admin/comment_flag/flag_detail.html', context)
