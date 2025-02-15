from django.urls import path

from . import views

app_name = "history"
urlpatterns = [path("<int:comment_id>/", views.detail, name="detail")]
