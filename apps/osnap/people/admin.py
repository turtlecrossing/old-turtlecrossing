# -*- coding: utf-8 -*-
"""
osnap.people.admin
==================
Administration for users.

:copyright: (C) 2013 Matthew Frazier
:license:   GNU GPL version 2 or later, see LICENSE for details
"""
from __future__ import unicode_literals
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AbstractUserAdmin
from django.utils.translation import ugettext_lazy as _

from .models import User

class UserAdmin(AbstractUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password', 'email')}),
        (_('Personal info'), {'fields': ('full_name', 'biography',
                                         'gravatar_email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    list_display = ('username', 'email', 'full_name', 'is_staff')
    list_display_links = ('username',)
    search_fields = ('username', 'full_name', 'email', 'biography')


admin.site.register(User, UserAdmin)

