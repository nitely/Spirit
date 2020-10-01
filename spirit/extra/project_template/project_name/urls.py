# -*- coding: utf-8 -*-

from django.conf.urls import include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin

import spirit.urls

# Override admin login for security purposes
from django.contrib.auth.decorators import login_required
admin.site.login = login_required(admin.site.login)


urlpatterns = [
    re_path(r'^', include(spirit.urls)),

    # This is the default django admin
    # it's not needed to use Spirit
    re_path(r'^admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
