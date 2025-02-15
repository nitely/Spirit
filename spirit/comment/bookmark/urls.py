from django.urls import path

from . import views

app_name = "bookmark"
urlpatterns = [
    path("<int:topic_id>/create/", views.create, name="create"),
    path("<int:topic_id>/find/", views.find, name="find"),
]
