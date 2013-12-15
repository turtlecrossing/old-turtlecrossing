# -*- coding: utf-8 -*-
"""
osnap.people.views
==================
Views for users to display and edit their profile.

:copyright: (C) 2013 Matthew Frazier
:license:   GNU GPL version 2 or later, see LICENSE for details
"""
from __future__ import unicode_literals
from django.views.generic import DetailView

from .models import User

class ProfileView(DetailView):
    model = User

    slug_field = 'username'
    slug_url_kwarg = 'username'

    template_name = 'osnap/people/profile.html'
    context_object_name = 'subject'

