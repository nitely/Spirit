from ...core.tags.registry import register
from .forms import LikeForm


@register.inclusion_tag('spirit/comment/like/_form.html')
def render_like_form(comment, like, next=None):
    form = LikeForm()
    return {'form': form, 'comment_id': comment.pk, 'like': like, 'next': next}
