"""

"""
from django.core.exceptions import ObjectDoesNotExist


def has_profile(user):
    try:
        profile = user.forum_profile
    except ObjectDoesNotExist:
        profile = None

    return profile is not None
