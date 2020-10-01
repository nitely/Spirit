# -*- coding: utf-8 -*-

from django.conf.urls import include, re_path

from ..views import register
from ..forms import RegistrationForm


class CustomRegisterForm(RegistrationForm):
    pass


def register_view(request):
    return register(request, registration_form=CustomRegisterForm)


urlpatterns = [
    re_path(r'^user/register/$', register_view, name='register'),
    re_path(r'^', include('spirit.urls')),
]
