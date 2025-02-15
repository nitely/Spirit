from ...core.tags.registry import register
from .forms import FavoriteForm
from .models import TopicFavorite


@register.inclusion_tag("spirit/topic/favorite/_form.html")
def render_favorite_form(topic, user, next=None):
    try:
        favorite = TopicFavorite.objects.get(user=user, topic=topic)
    except TopicFavorite.DoesNotExist:
        favorite = None

    form = FavoriteForm()
    return {"form": form, "topic_id": topic.pk, "favorite": favorite, "next": next}
