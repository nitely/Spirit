from django.urls import path

from . import views

app_name = "topic"
urlpatterns = [
    path("", views.deleted, name="index"),
    path("deleted/", views.deleted, name="deleted"),
    path("closed/", views.closed, name="closed"),
    path("pinned/", views.pinned, name="pinned"),
]
