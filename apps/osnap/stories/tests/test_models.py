from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.test import SimpleTestCase

from ..models import Story

class StoryModelTests(SimpleTestCase):
    def test_summaries(self):
        link = Story(title=u"Best Web site ever",
                     url=u"http://www.example.com/")

        self.assertEquals(str(link), u"Best Web site ever")
        self.assertEquals(link.domain, u"www.example.com")

        question = Story(title=u"How do I get into Red Hat Tower?",
                         text=u"I just wanted to see the Linux but "
                              u"the security guard threw me out. :-(")

        self.assertEquals(str(question), u"How do I get into Red Hat Tower?")
        self.assertEquals(question.domain, u"")

    def test_get_absolute_url(self):
        # Besides coverage, the main goal of testing this is to avoid
        # breaking links.
        link = Story(title=u"Best Web site ever",
                     url=u"http://www.example.com/",
                     id=555)

        self.assertEquals(link.get_absolute_url(), "/stories/555/")

    def test_content_types(self):
        story = Story(title=u"Best Web site ever")
        self.assertModelDoesNotValidate(story, 'neither_type')

        story.url = u"http://www.example.com/"
        self.assertModelValidates(story)

        story.text = u"Seriously, it's great."
        self.assertModelDoesNotValidate(story, 'both_types')

        story.url = u""
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

