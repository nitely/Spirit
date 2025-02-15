from django.urls import path

from . import views

app_name = "user"
urlpatterns = [
    path("", views.index, name="index"),
    path("admins/", views.index_admins, name="index-admins"),
    path("mods/", views.index_mods, name="index-mods"),
    path("unactive/", views.index_unactive, name="index-unactive"),
    path("edit/<int:user_id>/", views.edit, name="edit"),
]
