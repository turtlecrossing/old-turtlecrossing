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
from .views import ProfileView

urlpatterns = patterns('',
    url(
        regex=r"^~(?P<username>[a-zA-Z0-9_]+)/$",
        view=ProfileView.as_view(),
        name="osnap-profile"
    ),
)

