from django.urls import path
from django.urls import include

from . import views
import spirit.category.admin.urls
import spirit.comment.flag.admin.urls
import spirit.topic.admin.urls
import spirit.user.admin.urls


app_name = 'admin'
urlpatterns = [
    path('', views.dashboard, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('config/', views.config_basic, name='config-basic'),

    path('category/', include(spirit.category.admin.urls)),
    path('comment/flag/', include(spirit.comment.flag.admin.urls)),
    path('topic/', include(spirit.topic.admin.urls)),
    path('user/', include(spirit.user.admin.urls)),
]
