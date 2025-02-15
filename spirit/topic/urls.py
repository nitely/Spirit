from django.urls import include, path, re_path

import spirit.topic.favorite.urls
import spirit.topic.moderate.urls
import spirit.topic.notification.urls
import spirit.topic.private.urls
import spirit.topic.unread.urls

from . import views

app_name = "topic"
urlpatterns = [
    path("publish/", views.publish, name="publish"),
    path("publish/<int:category_id>/", views.publish, name="publish"),
    path("update/<int:pk>/", views.update, name="update"),
    path("<int:pk>/", views.detail, kwargs={"slug": ""}, name="detail"),
    re_path(r"^(?P<pk>[0-9]+)/(?P<slug>[\w-]+)/$", views.detail, name="detail"),
    path("active/", views.index_active, name="index-active"),
    path("moderate/", include(spirit.topic.moderate.urls)),
    path("unread/", include(spirit.topic.unread.urls)),
    path("notification/", include(spirit.topic.notification.urls)),
    path("favorite/", include(spirit.topic.favorite.urls)),
    path("private/", include(spirit.topic.private.urls)),
]
