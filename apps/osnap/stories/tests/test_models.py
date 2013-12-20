# -*- coding: utf-8 -*-
"""
osnap.stories.tests.test_models
===============================
These test custom Python code in our models.

:copyright: (C) 2013 Matthew Frazier
:license:   GNU GPL version 2 or later, see LICENSE for details
"""
from __future__ import unicode_literals
from django.test import SimpleTestCase

from snaketest import SnakeTestMixin

from ..models import Story

class StoryModelTests(SimpleTestCase, SnakeTestMixin):
    def test_summaries(self):
        link = Story(title="Best Web site ever",
                     url="http://www.example.com/")

        self.assert_str(link, "Best Web site ever")
        self.assert_equal(link.domain, "www.example.com")

        question = Story(title="How do I get into Red Hat Tower?",
                         text="I just wanted to see the Linux but "
                              "the security guard threw me out. :-(")

        self.assert_str(question, "How do I get into Red Hat Tower?")
        self.assert_equal(question.domain, "")

    def test_get_absolute_url(self):
        # Besides coverage, the main goal of testing this is to avoid
        # breaking links.
        link = Story(title="Best Web site ever",
                     url="http://www.example.com/",
                     id=555)

        self.assert_equal(link.get_absolute_url(), "/stories/555/")

    def test_content_types(self):
        story = Story(title="Best Web site ever")
        self.assert_not_model_validates(story, 'neither_type')

        story.url = "http://www.example.com/"
        self.assert_model_validates(story)

        story.text = "Seriously, it's great."
        self.assert_not_model_validates(story, 'both_types')

        story.url = ""
        self.assert_model_validates(story)

