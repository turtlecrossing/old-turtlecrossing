# -*- coding: utf-8 -*-
"""
democracy.tests.test_models_manager
===================================
These test Democracy's models and the managers associated with them.

:copyright: (C) 2013 Matthew Frazier
:license:   MIT/X11, see package's LICENSE for details
"""
from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models.query import QuerySet
from django.test import SimpleTestCase, TestCase

from snaketest import SnakeTestMixin

from ..models import Vote, VoteReason

from .democracytest.models import Cheese, CatPicture


class VoteModelTests(TestCase, SnakeTestMixin):
    fixtures = ['democracy_test_users', 'democracy_test_cheese']

    def test_vote_strings(self):
        calvin = User.objects.get(username='calvin')
        cheddar = Cheese.objects.get(variety='Cheddar')

        vote = Vote(user=calvin, item=cheddar, direction=1, reason="Tasty")
        self.assert_str(vote, "calvin's +1 Tasty to Cheddar")

        vote.reason = ""
        self.assert_str(vote, "calvin's +1 to Cheddar")

    def test_vote_validate_direction(self):
        calvin = User.objects.get(username='calvin')
        cheddar = Cheese.objects.get(variety='Cheddar')

        vote = Vote(user=calvin, item=cheddar, direction=3, reason="Tasty")
        self.assert_not_model_validates(vote, direction='invalid_choice')
        vote.direction = 0
        self.assert_not_model_validates(vote, direction='invalid_choice')
        vote.direction = -1
        self.assert_model_validates(vote)
        vote.direction = 1
        self.assert_model_validates(vote)

    def test_vote_get_user_vote(self):
        wesley = User.objects.get(username='wesley')
        cheddar = Cheese.objects.get(variety='Cheddar')

        vote = Vote.objects.get_user_vote(cheddar, wesley)
        self.assert_instance(vote, Vote)
        self.assert_fields_equal(vote, item=cheddar, direction=-1, reason="")

    def test_vote_get_user_vote_missing(self):
        calvin = User.objects.get(username='calvin')
        cheddar = Cheese.objects.get(variety='Cheddar')
        self.assert_none(Vote.objects.get_user_vote(cheddar, calvin))

    def test_vote_for_item(self):
        wesley = User.objects.get(username='wesley')
        arminius = User.objects.get(username='arminius')

        cheddar = Cheese.objects.get(variety='Cheddar')
        votes = Vote.objects.for_item(cheddar).order_by('user__username')

        self.assert_equal(len(votes), 2)
        self.assert_instances(votes, Vote)
        self.assert_fields_equal(votes[0], user=arminius, direction=1, reason="")
        self.assert_fields_equal(votes[1], user=wesley, direction=-1, reason="")

    def test_vote_for_item_none(self):
        gorgonzola = Cheese.objects.get(variety='Gorgonzola')
        votes = Vote.objects.for_item(gorgonzola)

        self.assert_instance(votes, QuerySet)
        self.assert_equal(len(votes), 0)


class VoteReasonModelTest(TestCase, SnakeTestMixin):
    def test_strings(self):
        ctype = ContentType.objects.get_for_model(Cheese)
        reason = VoteReason(direction=1, content_type=ctype)
        self.assert_str(reason, "+1 for cheeses")

        reason.reason = "Tasty"
        self.assert_str(reason, "+1 Tasty for cheeses")

    def test_validate_direction(self):
        ctype = ContentType.objects.get_for_model(Cheese)

        reason = VoteReason(direction=3, reason='Pungent', content_type=ctype)
        self.assert_not_model_validates(reason, direction='invalid_choice')
        reason.direction = 0
        self.assert_not_model_validates(reason, direction='invalid_choice')
        reason.direction = -1
        self.assert_model_validates(reason)
        reason.direction = 1
        self.assert_model_validates(reason)

    def test_for_model_downvotes(self):
        ctype = ContentType.objects.get_for_model(CatPicture)
        reason = VoteReason(direction=1, reason='Funny', content_type=ctype)
        reason.save()
        negative = VoteReason(direction=-1, reason='Not Funny', content_type=ctype)
        negative.save()

        # Cat pictures can't be downvoted, so only "Funny" should be returned.
        reasons = VoteReason.objects.get_for_model(CatPicture)
        self.assert_equal(len(reasons), 1)
        self.assert_fields_equal(reason, direction=1, reason='Funny')

    def test_for_model_none(self):
        # They might be cached heading into this method.
        reasons = VoteReason.objects.get_for_model(Cheese)
        self.assert_equal(reasons, ())

        # It should cache the reasons at this point.
        with self.assert_num_queries(0):
            reasons = VoteReason.objects.get_for_model(Cheese)
        self.assert_equal(reasons, ())

    def test_for_model_caching(self):
        ctype = ContentType.objects.get_for_model(Cheese)

        # Make sure they're cached.
        reasons = VoteReason.objects.get_for_model(Cheese)
        self.assert_equal(reasons, ())
        reasons = VoteReason.objects.get_for_model(CatPicture)
        self.assert_equal(reasons, ())

        # Save the new reason, make sure the cache is expired.
        reason = VoteReason(direction=1, reason='Sharp', content_type=ctype)
        reason.save()
        with self.assert_num_queries(1):
            reasons = VoteReason.objects.get_for_model(Cheese)
        self.assert_fields_equal(reasons[0], direction=1, reason='Sharp')

        # ...But only for Cheese.
        with self.assert_num_queries(0):
            reasons = VoteReason.objects.get_for_model(CatPicture)
        self.assert_equal(reasons, ())

        # Also, the cache needs to stay cached.
        with self.assert_num_queries(0):
            reasons = VoteReason.objects.get_for_model(Cheese)
        self.assert_fields_equal(reasons[0], direction=1, reason='Sharp')

        # Oh, deleting it should uncache too.
        reason.delete()
        with self.assert_num_queries(1):
            reasons = VoteReason.objects.get_for_model(Cheese)
        self.assert_equal(reasons, ())

        # Again, only for Cheese.
        with self.assert_num_queries(0):
            reasons = VoteReason.objects.get_for_model(CatPicture)
        self.assert_equal(reasons, ())

    def test_for_model_random(self):
        with self.assert_raises(TypeError):
            VoteReason.objects.get_for_model(User)

