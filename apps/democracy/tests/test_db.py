# -*- coding: utf-8 -*-
"""
democracy.tests.test_db
=======================
These test the overall operation of Democracy's database stuff.

:copyright: (C) 2013 Matthew Frazier
:license:   MIT/X11, see package's LICENSE for details
"""
from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test import SimpleTestCase, TestCase

from snaketest import SnakeTestMixin

from ..voting import Votable, VoteSettings, ObjectVotes
from ..models import Vote, VoteReason

from .democracytest.models import Cheese, CatPicture


class ModelTests(TestCase, SnakeTestMixin):
    fixtures = ['democracy_test_users']

    def test_vote_strings(self):
        maria = User.objects.get(username='calvin')
        cheddar = Cheese(variety="Cheddar")
        cheddar.save()

        vote = Vote(user=maria, item=cheddar, direction=1, reason="Tasty")
        self.assert_str(vote, "calvin's +1 Tasty to Cheddar")

        vote.reason = ""
        self.assert_str(vote, "calvin's +1 to Cheddar")

    def test_vote_validate_direction(self):
        maria = User.objects.get(username='calvin')
        cheddar = Cheese(variety="Cheddar")
        cheddar.save()

        vote = Vote(user=maria, item=cheddar, direction=3, reason="Tasty")
        self.assert_not_model_validates(vote, direction='invalid_choice')
        vote.direction = 0
        self.assert_not_model_validates(vote, direction='invalid_choice')
        vote.direction = -1
        self.assert_model_validates(vote)
        vote.direction = 1
        self.assert_model_validates(vote)

    def test_vote_reason_strings(self):
        ctype = ContentType.objects.get_for_model(Cheese)
        reason = VoteReason(direction=1, content_type=ctype)
        self.assert_str(reason, "+1 for cheeses")

        reason.reason = "Tasty"
        self.assert_str(reason, "+1 Tasty for cheeses")

    def test_vote_reason_validate_direction(self):
        ctype = ContentType.objects.get_for_model(Cheese)

        reason = VoteReason(direction=3, reason='Pungent', content_type=ctype)
        self.assert_not_model_validates(reason, direction='invalid_choice')
        reason.direction = 0
        self.assert_not_model_validates(reason, direction='invalid_choice')
        reason.direction = -1
        self.assert_model_validates(reason)
        reason.direction = 1
        self.assert_model_validates(reason)


class DefaultSettingTests(TestCase, SnakeTestMixin):
    def test_settings_classes(self):
        self.assert_instance(Cheese.votes, VoteSettings)
        self.assert_instance(CatPicture.votes, VoteSettings)

        self.assert_is(Cheese.votes.model, Cheese)
        self.assert_is(CatPicture.votes.model, CatPicture)

        self.assert_is(Cheese.votes.vote_model, Vote)
        self.assert_is(CatPicture.votes.vote_model, Vote)

    def test_scores(self):
        self.assert_equal(Cheese.votes.scores,
                          ('optimistic_score', 'pessimistic_score'))
        self.assert_equal(CatPicture.votes.scores, ('vote_count',))

    def test_votes_and_results(self):
        self.assert_true(Cheese.votes.downvotes_allowed)
        self.assert_true(Cheese.votes.use_reason_model)
        self.assert_equal(Cheese.votes.default_reasons, ((+1, ""), (-1, "")))

        ch_models = Cheese.votes.reasons
        self.assert_equal(len(ch_models), 2)
        self.assert_instances(ch_models, VoteReason)
        self.assert_fields_equal(ch_models[0], id=None, direction=1, reason="")
        self.assert_fields_equal(ch_models[1], id=None, direction=-1, reason="")

        self.assert_false(CatPicture.votes.downvotes_allowed)
        self.assert_true(CatPicture.votes.use_reason_model)
        self.assert_equal(CatPicture.votes.default_reasons, ((+1, ""),))

        cp_models = CatPicture.votes.reasons
        self.assert_equal(len(cp_models), 1)
        self.assert_instances(ch_models, VoteReason)
        self.assert_fields_equal(ch_models[0], id=None, direction=1, reason="")

