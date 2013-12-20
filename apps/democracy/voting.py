# -*- coding: utf-8 -*-
"""
democracy.voting
================
The code that you actually attach to models.

:copyright: (C) 2013 Matthew Frazier
:license:   MIT/X11, see package's LICENSE for details
"""
from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.db.models.loading import get_model
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import six
from django.utils import timezone

from .models import VoteReason


class Votable(object):
    """
    Put this on an object (and name it `votes`!) to allow users to vote on it.
    When you access `votes` on the class itself, it is a `VoteSettings`.
    When you access `votes` on an instance, it is an `ObjectVotes`.

    Pass all the parameters after `vote_model` as keyword arguments.

    :param vote_model:          The name of the model to store votes as.
                                This should inherit from `Vote`.
    :param downvotes_allowed:   Whether users should be able to downvote in
                                addition to upvote.
    :param use_reason_model:    If `True`, the app's user can store voting
                                reasons in `VoteReason`. If `False`, the
                                generic "+1/-1" or `reasons` list is used.
                                The default is `True`.
    :param reasons:             A set of default reasons to use if there are
                                none in the database. If `downvotes_allowed`,
                                these should be tuples of ``(+1|-1, reason)``,
                                otherwise just text strings.
    :param scores:              A list of "score" fields. These should
                                each have a corresponding `compute_score`
                                method, which will be called with the number
                                of upvotes and the number of downvotes
                                when votes are committed to update the fields.
                                They are guaranteed to be called in order.
    :param score:               You can use this if there's only one `score`.
    """
    def __init__(self, vote_model=None, downvotes_allowed=True,
                       use_reason_model=True, reasons=(),
                       scores=(), score=None):
        self._settings_cache = {}

        # We can't actually *load* the Vote model yet,
        # it might not yet be defined!
        if vote_model is not None:
            try:
                self._app_label, _self.model_name = vote_model.split(".")
            except ValueError:
                # If we can't split, assume a model in current app
                self._app_label = None
                self._model_name = relation
            except AttributeError:
                # If it doesn't have a split it's actually a model class
                self._app_label = vote_model._meta.app_label
                self._model_name = vote_model._meta.object_name
        else:
            self._app_label = 'democracy'
            self._model_name = 'Vote'

        self.downvotes_allowed = bool(downvotes_allowed)
        if downvotes_allowed:
            if reasons:
                valid = all(isinstance(reason, tuple) and
                                (reason[0] == 1 or reason[0] == -1) and
                                isinstance(reason[1], six.text_type)
                            for reason in reasons)
                if not valid:
                    raise ImproperlyConfigured("Reasons must be tuples of (+1|-1, text)")
            else:
                reasons = ((+1, ""), (-1, ""))
        else:
            if reasons:
                valid = all(isinstance(reason, six.text_type)
                            for reason in reasons)
                if not valid:
                    raise ImproperlyConfigured("Reasons must be text strings")
                reasons = tuple((+1, reason) for reason in reasons)
            else:
                reasons = ((+1, ""),)

        self.default_reasons = reasons
        self.use_reason_model = use_reason_model

        if scores and score:
            raise ImproperlyConfigured("Provide `score` or `scores`, but not both")
        elif score:
            self.scores = (score,)
        else:
            self.scores = tuple(scores)

    def __get__(self, instance, owner):
        if owner not in self._settings_cache:
            # Build a VoteSettings
            app_label = self._app_label or owner._meta.app_label
            vote_model = get_model(app_label, self._model_name)
            if vote_model is None:
                raise ImproperlyConfigured("Vote model %s.%s not found" %
                                           (app_label, self._model_name))

            self._settings_cache[owner] = VoteSettings(
                model=owner, vote_model=vote_model,
                downvotes_allowed=self.downvotes_allowed,
                scores=self.scores, default_reasons=self.default_reasons,
                use_reason_model=self.use_reason_model
            )

        if instance is None:
            return self._settings_cache[owner]
        else:
            return ObjectVotes(instance, self._settings_cache[owner])


class VoteSettings(object):
    """
    This is the object that actually appears when you access the `votes`
    property on a class. (Yay descriptors!)

    Don't create these yourself.
    """
    def __init__(self, model, vote_model, downvotes_allowed, scores,
                       default_reasons, use_reason_model):
        #: The model class itself.
        self.model = model

        #: The model class used for votes.
        self.vote_model = vote_model

        #: Whether downvotes are allowed or not.
        self.downvotes_allowed = downvotes_allowed

        #: A sequence of score attributes to update when votes happen.
        self.scores = scores

        #: A list of ``(+1|-1, reason)`` tuples for the default reason choices.
        #: If `use_reason_model` is `True`, these are only used if there
        #: are no VoteReasons in the database.
        #: If it's `False`, this is always used.
        self.default_reasons = default_reasons

        #: Whether to look up voting reasons in `VoteReason` or not.
        self.use_reason_model = use_reason_model

        # Create some fake VoteReason objects.
        ctype = ContentType.objects.get_for_model(model)

        self._default_reasons = tuple(
            VoteReason(content_type=ctype, direction=d, reason=r)
            for (d, r) in default_reasons
        )

    @property
    def reasons(self):
        """
        A list of `VoteReason` objects to use. Don't mess with them,
        as they might not be real!
        """
        if self.use_reason_model:
            reasons = VoteReason.objects.get_for_model(self.model)

            if reasons:
                return reasons
            else:
                return self._default_reasons
        else:
            return self._default_reasons


class ObjectVotes(object):
    """
    This is the object that actually appears when you access the `votes`
    property on an object. (Yay descriptors!)

    Don't create these yourself.
    """
    def __init__(self, item, settings):
        #: The `VoteSettings` object containing this object's settings.
        self.settings = settings
        #: The item these votes are about.
        self.item = item

        self.vote_model = settings.vote_model
        self.vote_objects = settings.vote_model.objects

    @property
    def reasons(self):
        """
        A list of `VoteReason` objects to use. Don't mess with them,
        as they might not be real!
        """
        return self.settings.reasons

    def get_user_vote(self, user):
        """
        Returns the vote a particular user has made on this object,
        or `None` if they have yet to vote.
        """
        return self.vote_objects.get_user_vote(self.item, user)

    def get_queryset(self):
        """
        Return a `QuerySet` of all the votes for this object.
        You can filter it and do whatever else you like.
        """
        return self.vote_objects.for_item(self.item)

    def get_vote_counts(self):
        """
        Return a tuple of ``(upvotes, downvotes)``. Both numbers are positive,
        and ineffective votes are not counted.
        """
        directions = self.get_queryset() \
            .filter(effective=True).values('direction') \
            .annotate(votes=models.Count('direction'))

        counts = dict((d['direction'], d['votes']) for d in directions)
        # Just ignore anything that's not 1 or -1.
        return counts.get(1, 0), counts.get(-1, 0)

    def get_reason_object(self, direction, reason=''):
        """
        Returns the reason object matching a `direction` and `reason`,
        or `None` if there is none.
        """
        if isinstance(direction, six.text_type):
            direction = int(direction, 10)
        if direction != 1 and direction != -1:
            raise ValueError("Only +1 or -1 can be directions")

        for obj in self.reasons:
            if obj.direction == direction and obj.reason == reason:
                return obj

        return None

    def add_vote(self, user, direction, reason=''):
        """
        Places a vote on this item, on behalf of a particular user.
        If the user has already voted, it overwrites their vote.

        :param user:        The user voting.
        :param direction:   The direction they're voting in -- +1 or -1.
        :param reason:      The voting reason.
        :raises ValueError: If the direction/reason combination is invalid.
        :return:            The new `AbstractVote` object.
        """
        reason_obj = self.get_reason_object(direction, reason)

        if reason_obj is None:
            raise ValueError("%s %s is not a valid voting reason" %
                             (direction, reason))

        # Should we just change an existing vote?
        vote = self.get_user_vote(user)
        if vote is None:
            # Create the Vote instance.
            vote = self.vote_model(item=self.item, user=user,
                                   direction=reason_obj.direction,
                                   reason=reason_obj.reason)
        else:
            # Update the vote. (Leave "effective" in place!)
            vote.direction = reason_obj.direction
            vote.reason = reason_obj.reason
            vote.placed_at = timezone.now()

        # Save the Vote instance.
        # The save() method automatically updates everything.
        vote.save()

        # Because Django doesn't have an identity map, the Vote may query a
        # fresh copy as its `item`, and so our `item` will stay unchanged.
        altered_item = vote.item
        for score in self.settings.scores:
            setattr(self.item, score, getattr(altered_item, score))

        return vote

    def remove_vote(self, user):
        """
        Removes a user's vote for a particular item.

        :param user:        The user voting.
        """
        # Is there a vote to remove?
        vote = self.get_user_vote(user)
        if vote is not None:
            # Okay, yes, there is.
            vote.delete()

        # See above for why I'm doing this.
        altered_item = vote.item
        for score in self.settings.scores:
            setattr(self.item, score, getattr(altered_item, score))

    def update_scores(self):
        """
        Recalculates the scores of the item, based on the current vote counts.
        Does not save the item.

        You should never need to call this yourself, as `AbstractVote`'s save
        and delete methods invoke this automatically. But if you do, call it
        within an `atomic` block.

        It returns a dict of the item's new scores.
        """
        votes = self.item.votes
        upvotes, downvotes = votes.get_vote_counts()
        new_scores = {}

        if self.settings.downvotes_allowed:
            # Call object.compute_score(upvotes, downvotes) for each score.
            for attr in self.settings.scores:
                compute_method = getattr(self.item, 'compute_' + attr)
                score = new_scores[attr] = compute_method(upvotes, downvotes)
                setattr(self.item, attr, score)
        else:
            # Call object.compute_score(upvotes) for each score.
            for attr in self.settings.scores:
                compute_method = getattr(self.item, 'compute_' + attr)
                score = new_scores[attr] = compute_method(upvotes)
                setattr(self.item, attr, score)

        return new_scores

