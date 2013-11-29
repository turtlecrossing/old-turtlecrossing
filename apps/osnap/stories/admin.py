"""
osnap.stories.admin
===================
Configuration for the Django admin interface.

:copyright: (C) 2013 Matthew Frazier
:license:   GNU GPL version 2 or later, see LICENSE for details
"""
from django.contrib import admin

from .models import Story

class StoryAdmin(admin.ModelAdmin):
    date_hierarchy = 'submit_date'
    list_display = ('submit_date', 'title', 'domain', 'submitter')
    list_display_links = ('title',)


admin.site.register(Story, StoryAdmin)

