# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url
from django.contrib.auth import views as django_views
from django.core.urlresolvers import reverse_lazy

from . import views


urlpatterns = [
    url(r'^login/$', views.custom_login, {'template_name': 'spirit/user/auth/login.html'}, name='user-login'),
    url(r'^logout/$', views.custom_logout, {'next_page': '/', }, name='user-logout'),

    url(r'^register/$', views.register, name='user-register'),
    url(r'^resend-activation/$', views.resend_activation_email, name='resend-activation'),

    url(r'^activation/(?P<pk>\d+)/(?P<token>[0-9A-Za-z_\-\.]+)/$', views.registration_activation,
        name='registration-activation'),

    url(r'^password-reset/$', views.custom_reset_password,
        {'template_name': 'spirit/user/auth/password_reset_form.html',
         'email_template_name': 'spirit/user/auth/password_reset_email.html',
         'subject_template_name': 'spirit/user/auth/password_reset_subject.txt',
         'post_reset_redirect': reverse_lazy('spirit:password-reset-done')},
        name='password-reset'),

    url(r'^password-reset/done/$', django_views.password_reset_done,
        {'template_name': 'spirit/user/auth/password_reset_done.html', },
        name='password-reset-done'),

    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[\w\-]+)/$', django_views.password_reset_confirm,
        {'template_name': 'spirit/user/auth/password_reset_confirm.html',
         'post_reset_redirect': reverse_lazy('spirit:password-reset-complete')},
        name='password-reset-confirm'),

    url(r'^reset/done/$', django_views.password_reset_complete,
        {'template_name': 'spirit/user/auth/password_reset_complete.html', },
        name='password-reset-complete'),
]
