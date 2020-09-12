# -*- coding: utf-8 -*-

import django.dispatch

search_index_update = django.dispatch.Signal(
    providing_args=['sender', 'instance'])
