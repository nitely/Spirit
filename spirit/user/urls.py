from django.urls import include, path, re_path

from . import views
from .auth import urls as auth_urls

app_name = "user"
urlpatterns = [
    path("", views.update, name="update"),
    path("password-change/", views.password_change, name="password-change"),
    path("email-change/", views.email_change, name="email-change"),
    re_path(
        r"^email-change/(?P<token>[0-9A-Za-z_\-\.]+)/$",
        views.email_change_confirm,
        name="email-change-confirm",
    ),
    re_path(
        r"^unsubscribe/(?P<pk>[0-9]+)/(?P<token>[0-9A-Za-z_\-\.]+)/$",
        views.unsubscribe,
        name="unsubscribe",
    ),
    path("<int:pk>/", views.comments, kwargs={"slug": ""}, name="detail"),
    re_path(r"^(?P<pk>[0-9]+)/(?P<slug>[\w-]+)/$", views.comments, name="detail"),
    path("topics/<int:pk>/", views.topics, kwargs={"slug": ""}, name="topics"),
    re_path(r"^topics/(?P<pk>[0-9]+)/(?P<slug>[\w-]+)/$", views.topics, name="topics"),
    path("likes/<int:pk>/", views.likes, kwargs={"slug": ""}, name="likes"),
    re_path(r"^likes/(?P<pk>[0-9]+)/(?P<slug>[\w-]+)/$", views.likes, name="likes"),
    path("menu/", views.menu, name="menu"),
    path("", include(auth_urls)),
]
