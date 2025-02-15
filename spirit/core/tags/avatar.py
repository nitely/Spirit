from .registry import register


@register.simple_tag()
def get_avatar_color(user_id):
    hue = (user_id % 37) * 10
    return f"hsl({hue}, 75%, 25%)"
