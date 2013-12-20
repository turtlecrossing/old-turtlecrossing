# -*- coding: utf-8 -*-
"""
turtlecrossing.settings.vanillatest
===================================
Settings which apply when testing reusable apps that need standard settings.

:copyright: (C) 2013 Matthew Frazier
:license:   GNU GPL version 2 or later, see LICENSE for details
"""
from __future__ import unicode_literals
from test import *

TESTING_APPS = (
    'democracy.tests.democracytest',
)

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + OUR_REUSABLE_APPS + TESTING_APPS

AUTH_USER_MODEL = 'auth.User'

