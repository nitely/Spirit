#-*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import HttpResponsePermanentRedirect
from django.utils.translation import ugettext as _
from django.conf import settings

from spirit.utils.ratelimit.decorators import ratelimit
from spirit import utils
from spirit.forms.comment import CommentForm
from spirit.signals.comment import comment_posted

from spirit.models.topic import Topic
from spirit.signals.topic import topic_viewed
from ..models.topic_private import TopicPrivate
from ..forms.topic_private import TopicPrivateManyForm, TopicForPrivateForm,\
    TopicPrivateJoinForm, TopicPrivateInviteForm
from spirit.signals.topic_private import topic_private_post_create, topic_private_access_pre_create


User = get_user_model()


@login_required
@ratelimit(rate='1/10s')
def private_publish(request, user_id=None):
    if request.method == 'POST':
        tform = TopicForPrivateForm(user=request.user, data=request.POST)
        cform = CommentForm(user=request.user, data=request.POST)
        tpform = TopicPrivateManyForm(user=request.user, data=request.POST)

        if not request.is_limited and tform.is_valid() and cform.is_valid() and tpform.is_valid():
            # wrap in transaction.atomic?
            topic = tform.save()
            cform.topic = topic
            comment = cform.save()
            comment_posted.send(sender=comment.__class__, comment=comment, mentions=None)
            tpform.topic = topic
            topics_private = tpform.save_m2m()
            topic_private_post_create.send(sender=TopicPrivate, topics_private=topics_private, comment=comment)
            return redirect(topic.get_absolute_url())

    else:
        tform = TopicForPrivateForm()
        cform = CommentForm()
        initial = None

        if user_id:
            user = get_object_or_404(User, pk=user_id)
            initial = {'users': [user.username, ]}

        tpform = TopicPrivateManyForm(initial=initial)

    return render(request, 'spirit/topic_private/private_publish.html', {'tform': tform,
                                                                         'cform': cform,
                                                                         'tpform': tpform})


@login_required
def private_detail(request, topic_id, slug):
    topic_private = get_object_or_404(TopicPrivate.objects.select_related('topic'),
                                      topic_id=topic_id, user=request.user)

    if topic_private.topic.slug != slug:
        return HttpResponsePermanentRedirect(topic_private.get_absolute_url())

    topic_viewed.send(sender=topic_private.topic.__class__, request=request, topic=topic_private.topic)

    return render(request, 'spirit/topic_private/private_detail.html', {'topic': topic_private.topic,
                                                                        'topic_private': topic_private,
                                                                        'COMMENTS_PER_PAGE': settings.ST_COMMENTS_PER_PAGE})


@login_required
@require_POST
def private_access_create(request, topic_id):
    topic_private = TopicPrivate.objects.for_create_or_404(topic_id, request.user)
    form = TopicPrivateInviteForm(topic=topic_private.topic, data=request.POST)

    if form.is_valid():
        topic_private_access_pre_create.send(sender=topic_private.__class__,
                                             topic=topic_private.topic,
                                             user=form.cleaned_data['user'])
        form.save()
    else:
        messages.error(request, utils.render_form_errors(form))

    return redirect(request.POST.get('next', topic_private.get_absolute_url()))


@login_required
def private_access_delete(request, pk):
    topic_private = TopicPrivate.objects.for_delete_or_404(pk, request.user)

    if request.method == 'POST':
        topic_private.delete()

        if request.user.pk == topic_private.user_id:
            return redirect(reverse("spirit:private-list"))

        return redirect(request.POST.get('next', topic_private.get_absolute_url()))
    else:
        return render(request, 'spirit/topic_private/private_delete.html', {'topic_private': topic_private, })


@login_required
def private_join(request, topic_id):
    # This is for topic creators who left their own topics and want to join again
    topic = get_object_or_404(Topic, pk=topic_id, user=request.user, category_id=settings.ST_TOPIC_PRIVATE_CATEGORY_PK)

    if request.method == 'POST':
        form = TopicPrivateJoinForm(topic=topic, user=request.user, data=request.POST)

        if form.is_valid():
            topic_private_access_pre_create.send(sender=TopicPrivate, topic=topic, user=request.user)
            form.save()

            return redirect(request.POST.get('next', topic.get_absolute_url()))
    else:
        form = TopicPrivateJoinForm()

    return render(request, 'spirit/topic_private/private_join.html', {'topic': topic, 'form': form, })


@login_required
def private_list(request):
    topics = Topic.objects.filter(topics_private__user=request.user).order_by('-last_active')
    return render(request, 'spirit/topic_private/private_list.html', {'topics': topics, })


@login_required
def private_created_list(request):
    # Show created topics but exclude those the user is participating on
    # TODO: show all, show join link in those the user is not participating
    topics = Topic.objects.filter(user=request.user, category_id=settings.ST_TOPIC_PRIVATE_CATEGORY_PK)\
        .exclude(topics_private__user=request.user)
    return render(request, 'spirit/topic_private/private_created_list.html', {'topics': topics, })