# -*- coding: utf-8 -*-

from django.urls import path
from django.urls import include

from ..views import register
from ..forms import RegistrationForm


class CustomRegisterForm(RegistrationForm):
    pass


def register_view(request):
    return register(request, registration_form=CustomRegisterForm)


urlpatterns = [
    path('user/register/', register_view, name='register'),
    path('', include('spirit.urls')),
]
