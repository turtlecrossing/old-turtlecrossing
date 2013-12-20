# -*- coding: utf-8 -*-
"""
democracy.tests.test_voting
===========================
These test the overall operation of Democracy
(at least, the parts I haven't moved into other files yet.)

:copyright: (C) 2013 Matthew Frazier
:license:   MIT/X11, see package's LICENSE for details
"""
from __future__ import unicode_literals
from django.test import SimpleTestCase, TestCase

from snaketest import SnakeTestMixin

from ..models import Vote, VoteReason
from ..voting import VoteSettings, ObjectVotes

from .democracytest.models import Cheese, CatPicture


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

