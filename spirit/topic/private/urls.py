from django.urls import path, re_path

from . import views

app_name = "private"
urlpatterns = [
    path("", views.index, name="index"),
    path("author/", views.index_author, name="index-author"),
    path("publish/", views.publish, name="publish"),
    path("publish/<int:user_id>/", views.publish, name="publish"),
    path("<int:topic_id>/", views.detail, kwargs={"slug": ""}, name="detail"),
    re_path(r"^(?P<topic_id>[0-9]+)/(?P<slug>[\w-]+)/$", views.detail, name="detail"),
    path("invite/<int:topic_id>/", views.create_access, name="access-create"),
    path("remove/<int:pk>/", views.delete_access, name="access-remove"),
    path("join/<int:topic_id>/", views.join_in, name="join"),
]
