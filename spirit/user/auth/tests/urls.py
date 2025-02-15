from django.urls import include, path

from ..forms import RegistrationForm
from ..views import register


class CustomRegisterForm(RegistrationForm):
    pass


def register_view(request):
    return register(request, registration_form=CustomRegisterForm)


urlpatterns = [
    path("user/register/", register_view, name="register"),
    path("", include("spirit.urls")),
]
