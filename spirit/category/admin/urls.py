from django.urls import path

from ...core.conf import settings
from . import views

app_name = "category"
urlpatterns = [
    path("", views.index, name="index"),
    path("create/", views.create, name="create"),
    path("update/<int:category_id>/", views.update, name="update"),
]

if settings.ST_ORDERED_CATEGORIES:
    urlpatterns.extend(
        [
            path("move-up/<int:category_id>/", views.move_up, name="move_up"),
            path("move-dn/<int:category_id>/", views.move_dn, name="move_dn"),
        ]
    )
