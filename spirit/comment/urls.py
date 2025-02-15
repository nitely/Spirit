from django.urls import include, path

import spirit.comment.bookmark.urls
import spirit.comment.flag.urls
import spirit.comment.history.urls
import spirit.comment.like.urls
import spirit.comment.poll.urls

from ..core.conf import settings
from . import views

app_name = "comment"
urlpatterns = [
    path("<int:topic_id>/publish/", views.publish, name="publish"),
    path("<int:topic_id>/publish/<int:pk>/quote/", views.publish, name="publish"),
    path("<int:pk>/update/", views.update, name="update"),
    path("<int:pk>/find/", views.find, name="find"),
    path("<int:topic_id>/move/", views.move, name="move"),
    path("<int:pk>/delete/", views.delete, name="delete"),
    path("<int:pk>/undelete/", views.delete, kwargs={"remove": False}, name="undelete"),
    path("bookmark/", include(spirit.comment.bookmark.urls)),
    path("flag/", include(spirit.comment.flag.urls)),
    path("history/", include(spirit.comment.history.urls)),
    path("like/", include(spirit.comment.like.urls)),
    path("poll/", include(spirit.comment.poll.urls)),
]

if settings.ST_UPLOAD_IMAGE_ENABLED:
    urlpatterns.append(
        path("upload/", views.image_upload_ajax, name="image-upload-ajax")
    )

if settings.ST_UPLOAD_FILE_ENABLED:
    urlpatterns.append(
        path("upload/file/", views.file_upload_ajax, name="file-upload-ajax")
    )
