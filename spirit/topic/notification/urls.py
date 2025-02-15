from django.urls import path

from . import views

app_name = "notification"
urlpatterns = [
    path("", views.index, name="index"),
    path("unread/", views.index_unread, name="index-unread"),
    path("ajax/", views.index_ajax, name="index-ajax"),
    path("<int:topic_id>/create/", views.create, name="create"),
    path("<int:pk>/update/", views.update, name="update"),
    path("mark/", views.mark_all_as_read, name="mark-all-as-read"),
]
