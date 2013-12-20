# -*- coding: utf-8 -*-
"""
osnap.people.tests.test_models
==============================
These test custom Python code in our models.

:copyright: (C) 2013 Matthew Frazier
:license:   GNU GPL version 2 or later, see LICENSE for details
"""
from __future__ import unicode_literals
from django.test import SimpleTestCase

from snaketest import SnakeTestMixin

from ..models import User

class UserModelTests(SimpleTestCase, SnakeTestMixin):
    def test_required_fields(self):
        user = User()
        user.set_password('correct horse battery staple')
        self.assert_not_model_validates(user, username='blank', email='blank')

        user.username = 'loner'
        self.assert_not_model_validates(user, email='blank')

        user.email = 'loneranger@example.com'
        self.assert_model_validates(user)

    def test_full_names_usernames(self):
        user = User(username='loner')
        self.assertEquals(user.get_short_name(), 'loner')
        self.assertEquals(user.get_full_name(),  'loner')

        user.full_name = 'Lone Ranger'
        self.assertEquals(user.get_short_name(), 'loner')
        self.assertEquals(user.get_full_name(),  'Lone Ranger')

