# -*- coding: utf-8 -*-

from django.core.wsgi import get_wsgi_application


# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings.local_prod")
application = get_wsgi_application()