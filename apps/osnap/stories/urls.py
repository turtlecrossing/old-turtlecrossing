# -*- coding: utf-8 -*-
"""
osnap.stories.urls
==================
A default URLConf. Aside from the front page, this all uses ``stories/``
as a prefix. (I may need to rethink this in the future.)

:copyright: (C) 2013 Matthew Frazier
:license:   GNU GPL version 2 or later, see LICENSE for details
"""
from __future__ import unicode_literals
from django.conf.urls import patterns
from django.conf.urls import url

from .views import FrontPageView, StoryDetailView, SubmitStoryView

urlpatterns = patterns("",
    url(
        regex=r"^$",
        view=FrontPageView.as_view(),
        name="osnap_front_page"
    ),
    url(
        regex=r"^stories/(?P<id>\d+)/$",
        view=StoryDetailView.as_view(),
        name="osnap_story_detail"
    ),
    url(
        regex=r"^stories/submit/$",
        view=SubmitStoryView.as_view(),
        name="osnap_story_submit"
    ),
)

