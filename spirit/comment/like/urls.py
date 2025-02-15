from django.urls import path

from . import views

app_name = "like"
urlpatterns = [
    path("<int:comment_id>/create/", views.create, name="create"),
    path("<int:pk>/delete/", views.delete, name="delete"),
]
