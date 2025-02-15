from django.urls import path, re_path

from . import views

app_name = "auth"
urlpatterns = [
    path("login/", views.custom_login, name="login"),
    path("logout/", views.custom_logout, name="logout"),
    path("register/", views.register, name="register"),
    path("resend-activation/", views.resend_activation_email, name="resend-activation"),
    re_path(
        r"^activation/(?P<pk>[0-9]+)/(?P<token>[0-9A-Za-z_\-\.]+)/$",
        views.registration_activation,
        name="registration-activation",
    ),
    path("password-reset/", views.custom_password_reset, name="password-reset"),
    path(
        "password-reset/done/",
        views.custom_password_reset_done,
        name="password-reset-done",
    ),
    re_path(
        r"^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[\w\-]+)/$",
        views.custom_password_reset_confirm,
        name="password-reset-confirm",
    ),
    path(
        "reset/done/",
        views.custom_password_reset_complete,
        name="password-reset-complete",
    ),
]
