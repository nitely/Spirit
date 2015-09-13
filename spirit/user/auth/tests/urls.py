# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import include, url

from ..views import register
from ..forms import RegistrationForm


class CustomRegisterForm(RegistrationForm):
    pass


def register_view(request):
    return register(request, registration_form=CustomRegisterForm)


urlpatterns = [
    url(r'^user/register/$', register_view, name='register'),
    url(r'^', include('spirit.urls')),
]
