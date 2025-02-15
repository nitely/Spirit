from django.urls import path

from . import views

app_name = "flag"
urlpatterns = [
    path("", views.opened, name="index"),
    path("opened/", views.opened, name="opened"),
    path("closed/", views.closed, name="closed"),
    path("<int:pk>/", views.detail, name="detail"),
]
