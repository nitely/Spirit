from django.urls import path

from . import views

app_name = "moderate"
urlpatterns = [
    path("delete/<int:pk>/", views.delete, name="delete"),
    path("undelete/<int:pk>/", views.undelete, name="undelete"),
    path("lock/<int:pk>/", views.lock, name="lock"),
    path("unlock/<int:pk>/", views.unlock, name="unlock"),
    path("pin/<int:pk>/", views.pin, name="pin"),
    path("unpin/<int:pk>/", views.unpin, name="unpin"),
    path("global-pin/<int:pk>/", views.global_pin, name="global-pin"),
    path("global-unpin/<int:pk>/", views.global_unpin, name="global-unpin"),
]
