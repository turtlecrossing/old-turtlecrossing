# -*- coding: utf-8 -*-
"""
osnap.people.urls
=================
All the account-related URL's.

:copyright: (C) 2013 Matthew Frazier
:license:   GNU GPL version 2 or later, see LICENSE for details
"""
from __future__ import unicode_literals
from django.conf.urls import patterns, include, url
from django.contrib.auth import views as auth_views
from .views import ProfileView, RegisterView, activate_account


account_urls = patterns('',
    # Login, Logout
    url(
        regex=r'^login/$',
        view=auth_views.login,
        kwargs={'template_name': 'osnap/accounts/login.html'},
        name='accounts_login'
    ),
    url(
        regex=r'^logout/$',
        view=auth_views.logout,
        kwargs={'template_name': 'osnap/accounts/done.html',
                'extra_context': {'action': 'logged out'}},
        name='accounts_logout'
    ),

    # Registration, Activation
    url(
        regex=r'^register/$',
        view=RegisterView.as_view(),
        name='accounts_register'
    ),
    url(
        regex=r'^activate/(?P<token>.+)/$',
        view=activate_account,
        name='accounts_activate'
    ),

    # Reset Password
    url(
        regex=r'^password/reset/$',
        view=auth_views.password_reset,
        kwargs={'template_name': 'osnap/accounts/password-reset/request.html',
                'email_template_name': 'osnap/accounts/password-reset/email.txt',
                'subject_template_name': 'osnap/accounts/password-reset/email-subject.txt'},
        name='accounts_password_reset'
    ),
    url(
        regex=r'^password/reset/done/$',
        view=auth_views.password_reset_done,
        kwargs={'template_name': 'osnap/accounts/done.html',
                'extra_context': {'action': 'password reset requested'}},
        name='password_reset_done'
    ),
    url(
        regex=r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        view=auth_views.password_reset_confirm,
        kwargs={'template_name': 'osnap/accounts/password-reset/confirm.html'},
        name='accounts_password_reset_confirm'
    ),
    url(
        regex=r'^password/reset/complete/$',
        view=auth_views.password_reset_complete,
        kwargs={'template_name': 'osnap/accounts/done.html',
                'extra_context': {'action': 'password reset'}},
        name='password_reset_complete'
    ),
)


urlpatterns = patterns('',
    url(
        regex=r"^~(?P<username>[a-zA-Z0-9_]+)/$",
        view=ProfileView.as_view(),
        name="osnap_profile"
    ),

    url('^accounts/', include(account_urls)),
)

