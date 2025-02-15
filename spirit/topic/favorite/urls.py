from django.urls import path

from . import views

app_name = "favorite"
urlpatterns = [
    path("<int:topic_id>/create/", views.create, name="create"),
    path("<int:pk>/delete/", views.delete, name="delete"),
]
