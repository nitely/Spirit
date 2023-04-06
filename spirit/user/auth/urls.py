# -*- coding: utf-8 -*-

from django.urls import re_path

from . import views


app_name = 'auth'
urlpatterns = [
    re_path(r'^login/$', views.custom_login, name='login'),
    re_path(r'^logout/$', views.custom_logout, name='logout'),

    re_path(r'^register/$', views.register, name='register'),
    re_path(r'^resend-activation/$',
        views.resend_activation_email,
        name='resend-activation'),

    re_path(r'^activation/(?P<pk>[0-9]+)/(?P<token>[0-9A-Za-z_\-\.]+)/$',
        views.registration_activation,
        name='registration-activation'),
    re_path(r'^password-reset/$', views.custom_password_reset, name='password-reset'),
    re_path(r'^password-reset/done/$',
        views.custom_password_reset_done,
        name='password-reset-done'),
    re_path(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[\w\-]+)/$',
        views.custom_password_reset_confirm,
        name='password-reset-confirm'),
    re_path(r'^reset/done/$',
        views.custom_password_reset_complete,
        name='password-reset-complete')
]
