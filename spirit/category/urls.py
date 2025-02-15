from django.urls import path, re_path

from . import views

app_name = "category"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("<int:pk>/", views.detail, kwargs={"slug": ""}, name="detail"),
    re_path(r"^(?P<pk>[0-9]+)/(?P<slug>[\w-]+)/$", views.detail, name="detail"),
]
