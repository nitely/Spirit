#-*- coding: utf-8 -*-

from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.translation import ugettext as _

from spirit.utils.decorators import administrator_required

from spirit.models.comment_flag import CommentFlag, Flag
from spirit.forms.admin import CommentFlagForm


@administrator_required
def flag_open(request):
    flags = CommentFlag.objects.filter(is_closed=False)
    return render(request, 'spirit/admin/comment_flag/flag_open.html', {'flags': flags, })


@administrator_required
def flag_closed(request):
    flags = CommentFlag.objects.filter(is_closed=True)
    return render(request, 'spirit/admin/comment_flag/flag_closed.html', {'flags': flags, })


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

    flags = Flag.objects.filter(comment=flag.comment)
    return render(request, 'spirit/admin/comment_flag/flag_detail.html', {'flag': flag,
                                                                          'flags': flags,
                                                                          'form': form})