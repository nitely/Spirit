from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin

# Override admin login for security purposes
from django.contrib.auth.decorators import login_required
from django.urls import include, path, re_path

import spirit.urls

admin.site.login = login_required(admin.site.login)


urlpatterns = [
    path("", include(spirit.urls)),
    # This is the default django admin
    # it's not needed to use Spirit
    re_path(r"^admin/", admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
