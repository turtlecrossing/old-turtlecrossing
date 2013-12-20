# -*- coding: utf-8 -*-
"""
democracy.managers
==================
Additional database support for our models.

:copyright: (C) 2013 Matthew Frazier
:license:   MIT/X11, see package's LICENSE for details
"""
from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_save, post_delete


class VoteReasonManager(models.Manager):
    """
    This is a manager for `VoteReason`. You don't need to do anything
    fancy with it.
    """
    def __init__(self, *args, **kwargs):
        super(VoteReasonManager, self).__init__(*args, **kwargs)
        self._reason_cache = {}

    def contribute_to_class(self, model_cls, name):
        super(VoteReasonManager, self).contribute_to_class(model_cls, name)

        post_save.connect(self._clear_reason_cache, sender=model_cls)
        post_delete.connect(self._clear_reason_cache, sender=model_cls)

    def _clear_reason_cache(self, sender, **kwargs):
        if 'instance' in kwargs:
            model = kwargs['instance'].content_type.model_class()
            if model in self._reason_cache:
                del self._reason_cache[model]

    def get_for_model(self, model):
        """
        Gets the voting reasons in the database for a particular model class.

        :param model:   The model to grab.
        :return:        A list of `VoteReason` objects.
        """
        if model in self._reason_cache:
            return self._reason_cache[model]

        vote_settings = getattr(model, 'votes', None)

        # Circular dependencies :-(
        from .voting import VoteSettings
        if not isinstance(vote_settings, VoteSettings):
            raise TypeError("Models must have a Votable named 'votes'")

        ctype = ContentType.objects.get_for_model(model)

        qset = self.filter(content_type__id=ctype.id)
        if not vote_settings.downvotes_allowed:
            # Silently drop downvotes so we don't have to worry about it.
            qset = qset.filter(direction=1)

        reasons = self._reason_cache[model] = tuple(qset)
        return reasons


class VoteManager(models.Manager):
    """
    This is a manager for `Vote`.

    If you have a custom `AbstractVote` subclass, you will need to implement
    each of these methods as well. But otherwise, we don't do anything
    fancy with the managers.
    """
    def get_user_vote(self, item, user):
        """
        Returns a particular user's `Vote` on an item, or `None` if they
        have not yet voted.
        """
        ctype = ContentType.objects.get_for_model(item)
        try:
            return self.get(content_type__pk=ctype.id, object_id=item.id,
                            user=user)
        except models.ObjectDoesNotExist:
            return None

    def for_item(self, item):
        """
        Returns a `QuerySet` of votes for a particular item, not in any
        particular order.
        """
        ctype = ContentType.objects.get_for_model(item)
        return self.filter(content_type__pk=ctype.id, object_id=item.id)

