# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from spirit.templatetags.registry import register
from .models import TopicFavorite
from .forms import FavoriteForm


@register.inclusion_tag('spirit/topic/favorite/_form.html')
def render_favorite_form(topic, user, next=None):
    try:
        favorite = TopicFavorite.objects.get(user=user, topic=topic)
    except TopicFavorite.DoesNotExist:
        favorite = None

    form = FavoriteForm()
    return {'form': form, 'topic_id': topic.pk, 'favorite': favorite, 'next': next}
