# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.translation import ugettext as _
from djconfig import config

from spirit.utils.paginator import yt_paginate
from spirit.utils.decorators import administrator_required
from .forms import CommentFlagForm
from ..models import CommentFlag, Flag


@administrator_required
def detail(request, pk):
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

    return render(request, 'spirit/comment/flag/admin/detail.html', context)


@administrator_required
def _index(request, queryset, template):
    flags = yt_paginate(
        queryset,
        per_page=config.comments_per_page,
        page_number=request.GET.get('page', 1)
    )
    context = {'flags': flags, }
    return render(request, template, context)


def opened(request):
    return _index(
        request,
        queryset=CommentFlag.objects.filter(is_closed=False),
        template='spirit/comment/flag/admin/open.html'
    )


def closed(request):
    return _index(
        request,
        queryset=CommentFlag.objects.filter(is_closed=True),
        template='spirit/comment/flag/admin/closed.html'
    )