# -*- coding: utf-8 -*-
"""
democracy.tests.democracytest.models
====================================
Models that we use to test Democracy's database stuff.
This app is about theologians voting on cheeses and cat pictures.

:copyright: (C) 2013 Matthew Frazier
:license:   MIT/X11, see package's LICENSE for details
"""
from __future__ import unicode_literals
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from ...voting import Votable

@python_2_unicode_compatible
class Cheese(models.Model):
    variety = models.CharField(max_length=30, unique=True)
    optimistic_score = models.IntegerField(default=1)
    pessimistic_score = models.IntegerField(default=1)

    votes = Votable(scores=('optimistic_score', 'pessimistic_score'))

    def compute_optimistic_score(self, upvotes, downvotes):
        return 1 + 2 * upvotes - downvotes

    def compute_pessimistic_score(self, upvotes, downvotes):
        return 1 + upvotes - 2 * downvotes

    def __str__(self):
        return self.variety


class CatPicture(models.Model):
    caption = models.CharField(max_length=64)
    vote_count = models.IntegerField(default=0)

    votes = Votable(score='vote_count', downvotes_allowed=False)

    def compute_vote_count(self, upvotes, downvotes):
        return upvotes

