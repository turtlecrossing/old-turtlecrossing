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
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models.query import QuerySet
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


class ObjectVotesTests(TestCase, SnakeTestMixin):
    fixtures = ['democracy_test_users', 'democracy_test_cheese', 'democracy_test_cats']

    def test_get_user_vote(self):
        wesley = User.objects.get(username='wesley')
        calvin = User.objects.get(username='calvin')
        cheddar = Cheese.objects.get(variety='Cheddar')

        vote = cheddar.votes.get_user_vote(wesley)
        self.assert_instance(vote, Vote)
        self.assert_fields_equal(vote, item=cheddar, direction=-1, reason="")

        self.assert_none(cheddar.votes.get_user_vote(calvin))

    def test_get_queryset(self):
        cheddar = Cheese.objects.get(variety='Cheddar')
        votes = cheddar.votes.get_queryset()
        self.assert_instance(votes, QuerySet)
        self.assert_equal(len(votes), 2)

    def test_count_votes(self):
        # Arminius voted up, Wesley voted down.
        cheddar = Cheese.objects.get(variety='Cheddar')
        self.assert_equal(cheddar.votes.get_vote_counts(), (1, 1))

        # Wesley voted up, and Calvin's upvote is not efficient.
        brie = Cheese.objects.get(variety='Brie')
        self.assert_equal(brie.votes.get_vote_counts(), (1, 0))

        # Nobody voted.
        gorgonzola = Cheese.objects.get(variety='Gorgonzola')
        self.assert_equal(gorgonzola.votes.get_vote_counts(), (0, 0))

    def test_get_reason(self):
        ctype = ContentType.objects.get_for_model(Cheese)
        cheddar = Cheese.objects.get(variety='Cheddar')

        up = cheddar.votes.get_reason_object(1)
        self.assert_fields_equal(up, content_type=ctype, direction=1, reason='')
        self.assert_none(cheddar.votes.get_reason_object(1, 'Pungent'))

        reason = VoteReason(direction=1, reason='Pungent', content_type=ctype)
        reason.save()

        pungent = cheddar.votes.get_reason_object(1, 'Pungent')
        self.assert_fields_equal(pungent, content_type=ctype, direction=1, reason='Pungent')
        self.assert_none(cheddar.votes.get_reason_object(1))
        self.assert_none(cheddar.votes.get_reason_object(-1))

        # Somehow the Pungent is surviving...
        pungent.delete()

    def test_get_reason_strings(self):
        ctype = ContentType.objects.get_for_model(Cheese)
        cheddar = Cheese.objects.get(variety='Cheddar')

        up = cheddar.votes.get_reason_object("+1")
        self.assert_fields_equal(up, content_type=ctype, direction=1, reason='')

        up_unsigned = cheddar.votes.get_reason_object("1")
        self.assert_is(up_unsigned, up)

        down = cheddar.votes.get_reason_object("-1")
        self.assert_fields_equal(down, content_type=ctype, direction=-1, reason='')

        self.assert_none(cheddar.votes.get_reason_object("+1", 'Pungent'))
        self.assert_none(cheddar.votes.get_reason_object("-1", 'Moldy'))

        with self.assert_raises(ValueError):
            cheddar.votes.get_reason_object("+3")
        with self.assert_raises(ValueError):
            cheddar.votes.get_reason_object("up")
        with self.assert_raises(ValueError):
            cheddar.votes.get_reason_object(None)
        with self.assert_raises(ValueError):
            cheddar.votes.get_reason_object("")
        with self.assert_raises(ValueError):
            cheddar.votes.get_reason_object(0)

    def test_update_scores(self):
        cheddar = Cheese.objects.get(variety='Cheddar')
        cheddar.optimistic_score = 0
        cheddar.pessimistic_score = 0

        cheddar.votes.update_scores()
        # Right now, Wesley and Arminius are equally matched.
        self.assert_equal(cheddar.optimistic_score, 2)      # 1 + 2 - 1
        self.assert_equal(cheddar.pessimistic_score, 0)     # 1 + 1 - 2

        brie = CatPicture.objects.get(pk=1)
        brie.vote_count = 3
        brie.votes.update_scores()
        # All three theologians voted for this one.
        self.assert_equal(brie.vote_count, 90)

    def test_add_remove_vote(self):
        calvin = User.objects.get(username='calvin')
        cheddar = Cheese.objects.get(variety='Cheddar')
        self.assert_none(cheddar.votes.get_user_vote(calvin))

        # Calvin votes for Cheddar.
        vote = cheddar.votes.add_vote(calvin, +1)
        self.assert_equal(vote.direction, +1)
        self.assert_equal(vote.reason, '')
        self.assert_is(vote.effective, True)

        self.assert_equal(cheddar.votes.get_vote_counts(), (2, 1))
        self.assert_equal(cheddar.optimistic_score, 4)      # 1 + 4 - 1
        self.assert_equal(cheddar.pessimistic_score, 1)     # 1 + 2 - 2

        # Then he decides he doesn't like Cheddar.
        new_vote = cheddar.votes.add_vote(calvin, -1)
        self.assert_equal(new_vote.id, vote.id)
        self.assert_equal(new_vote.direction, -1)
        self.assert_equal(new_vote.reason, '')
        self.assert_is(new_vote.effective, True)

        self.assert_equal(cheddar.votes.get_vote_counts(), (1, 2))
        self.assert_equal(cheddar.optimistic_score, 1)      # 1 + 2 - 2
        self.assert_equal(cheddar.pessimistic_score, -2)    # 1 + 1 - 4

        # Then he decides to stay out of it entirely.
        cheddar.votes.remove_vote(calvin)
        self.assert_none(cheddar.votes.get_user_vote(calvin))

        self.assert_equal(cheddar.votes.get_vote_counts(), (1, 1))
        self.assert_equal(cheddar.optimistic_score, 2)      # 1 + 2 - 1
        self.assert_equal(cheddar.pessimistic_score, 0)     # 1 + 1 - 2

