# -*- coding: utf-8 -*-
"""
osnap.people.tests.test_models
==============================
These test custom Python code in our models.

:copyright: (C) 2013 Matthew Frazier
:license:   GNU GPL version 2 or later, see LICENSE for details
"""
from __future__ import unicode_literals
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.test import SimpleTestCase
from django.utils import six

from ..models import User

class UserModelTests(SimpleTestCase):
    def test_required_fields(self):
        user = User()
        user.set_password('correct horse battery staple')
        self.assertModelDoesNotValidate(user, username='blank')

        user.username = 'loner'
        self.assertModelValidates(user)

    def test_full_names_usernames(self):
        user = User(username='loner')
        self.assertEquals(user.get_short_name(), 'loner')
        self.assertEquals(user.get_full_name(),  'loner')

        user.full_name = 'Lone Ranger'
        self.assertEquals(user.get_short_name(), 'loner')
        self.assertEquals(user.get_full_name(),  'Lone Ranger')

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

            if isinstance(codes, six.string_types):
                codes = set([codes])
            else:
                codes = set(codes)

            self.assertEquals(
                set(error.code for error in errors[field]),
                codes
            )

