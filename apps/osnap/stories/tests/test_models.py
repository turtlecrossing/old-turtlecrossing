# -*- coding: utf-8 -*-
"""
osnap.stories.tests.test_models
===============================
These test custom Python code in our models.

:copyright: (C) 2013 Matthew Frazier
:license:   GNU GPL version 2 or later, see LICENSE for details
"""
from __future__ import unicode_literals
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.test import SimpleTestCase

from ..models import Story

class StoryModelTests(SimpleTestCase):
    def test_summaries(self):
        link = Story(title="Best Web site ever",
                     url="http://www.example.com/")

        self.assertEquals(str(link), "Best Web site ever")
        self.assertEquals(link.domain, "www.example.com")

        question = Story(title="How do I get into Red Hat Tower?",
                         text="I just wanted to see the Linux but "
                              "the security guard threw me out. :-(")

        self.assertEquals(str(question), "How do I get into Red Hat Tower?")
        self.assertEquals(question.domain, "")

    def test_get_absolute_url(self):
        # Besides coverage, the main goal of testing this is to avoid
        # breaking links.
        link = Story(title="Best Web site ever",
                     url="http://www.example.com/",
                     id=555)

        self.assertEquals(link.get_absolute_url(), "/stories/555/")

    def test_content_types(self):
        story = Story(title="Best Web site ever")
        self.assertModelDoesNotValidate(story, 'neither_type')

        story.url = "http://www.example.com/"
        self.assertModelValidates(story)

        story.text = "Seriously, it's great."
        self.assertModelDoesNotValidate(story, 'both_types')

        story.url = ""
        self.assertModelValidates(story)

    ### Helpers - to be ported to a reusable app

    def assertModelValidates(self, model):
        model.full_clean()

    def assertModelDoesNotValidate(self, model, *all_codes, **field_codes):
        with self.assertRaises(ValidationError) as caught:
            model.full_clean()

        errors = caught.exception.error_dict
        if all_codes:
            self.assertEquals(len(errors), 1 + len(field_codes))
            self.assertIn(NON_FIELD_ERRORS, errors)
            self.assertEquals(
                set(error.code for error in errors[NON_FIELD_ERRORS]),
                set(all_codes)
            )
        else:
            self.assertEquals(len(errors), len(field_codes))

        for field, codes in field_codes.items():
            self.assertIn(field, errors)

            if isinstance(codes, str):
                codes = set([codes])
            else:
                codes = set(codes)

            self.assertEquals(
                set(error.code for error in errors[field]),
                codes
            )

