# -*- coding: utf-8 -*-

from django.db import transaction, IntegrityError


def create_or_none(cls, **kwargs):
    """
    Return the saved model instance if it was created, \
    return ``None`` otherwise
    """
    try:
        with transaction.atomic():
            return cls.objects.create(**kwargs)
    except IntegrityError:
        return None
