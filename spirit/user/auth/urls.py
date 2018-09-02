# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url

from . import views


app_name = 'auth'
urlpatterns = [
    url(r'^login/$', views.custom_login, name='login'),
    url(r'^logout/$', views.custom_logout, name='logout'),

    url(r'^register/$', views.register, name='register'),
    url(r'^resend-activation/$',
        views.resend_activation_email,
        name='resend-activation'),

    url(r'^activation/(?P<pk>[0-9]+)/(?P<token>[0-9A-Za-z_\-\.]+)/$',
        views.registration_activation,
        name='registration-activation'),
    url(r'^password-reset/$', views.custom_password_reset, name='password-reset'),
    url(r'^password-reset/done/$',
        views.custom_password_reset_done,
        name='password-reset-done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[\w\-]+)/$',
        views.custom_password_reset_confirm,
        name='password-reset-confirm'),
    url(r'^reset/done/$',
        views.custom_password_reset_complete,
        name='password-reset-complete')
]
