from django.urls import path

from . import views

app_name = "flag"
urlpatterns = [path("<int:comment_id>/create/", views.create, name="create")]
