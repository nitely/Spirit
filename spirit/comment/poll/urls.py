from django.urls import path

from . import views

app_name = "poll"
urlpatterns = [
    path("close/<int:pk>/", views.close_or_open, name="close"),
    path("open/<int:pk>/", views.close_or_open, kwargs={"close": False}, name="open"),
    path("vote/<int:pk>/", views.vote, name="vote"),
    path("voters/<int:pk>/", views.voters, name="voters"),
]
