"""
osnap.stories.forms
===================
Forms used for story submission, editing, etc.

:copyright: (C) 2013 Matthew Frazier
:license:   GNU GPL version 2 or later, see LICENSE for details
"""
from django import forms

from .models import Story

class StorySubmitForm(forms.ModelForm):
    class Meta:
        model = Story
        fields = ['title', 'url', 'text']

