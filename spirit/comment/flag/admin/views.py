from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.utils.translation import gettext as _

from djconfig import config

from spirit.core.utils.views import is_post, post_data
from spirit.core.utils.paginator import yt_paginate
from spirit.core.utils.decorators import administrator_required
from .forms import CommentFlagForm
from ..models import CommentFlag, Flag


@administrator_required
def detail(request, pk):
    flag = get_object_or_404(CommentFlag, pk=pk)
    form = CommentFlagForm(
        user=request.user,
        data=post_data(request),
        instance=flag)

    if is_post(request) and form.is_valid():
        form.save()
        messages.info(request, _("The flag has been moderated!"))
        return redirect(reverse("spirit:admin:flag:index"))

    flags = yt_paginate(
        Flag.objects.filter(comment=flag.comment),
        per_page=config.comments_per_page,
        page_number=request.GET.get('page', 1)
    )

    return render(
        request=request,
        template_name='spirit/comment/flag/admin/detail.html',
        context={
            'flag': flag,
            'flags': flags,
            'form': form})


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
