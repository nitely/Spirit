from django.urls import path

from . import views

app_name = "unread"
urlpatterns = [path("", views.index, name="index")]
