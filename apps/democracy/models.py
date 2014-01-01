# -*- coding: utf-8 -*-
"""
democracy.models
================
Database models that store voting information.

:copyright: (C) 2013 Matthew Frazier
:license:   MIT/X11, see package's LICENSE for details
"""
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from .managers import VoteManager, VoteReasonManager
from .signals import pre_vote, post_vote, pre_remove_vote, post_remove_vote


VOTE_DIRECTIONS = (
    (+1,    '+1'),
    (-1,    '-1')
)


@python_2_unicode_compatible
class VoteReason(models.Model):
    """
    A reason to vote for an item. When these are set for a particular
    content type, the user has a choice of options such as "+1 Insightful,"
    "-1 Offensive," etc.

    When none are set, the user gets generic "+1" and "-1" options,
    depending on the content type's upvote/downvote settings.

    There is intentionally not foreign-keyed from AbstractVote, primarily
    because these are intended to be loaded from fixtures yet
    change over time. The voting system does check to make sure that
    all reasons are valid at the time of entry.
    """
    REASON_LENGTH = 32

    objects = VoteReasonManager()

    content_type = models.ForeignKey(ContentType,
                    verbose_name=_("content type"),
                    help_text=_("The kind of item that this reason can be "
                                "used to vote on."))

    direction   = models.SmallIntegerField(_("direction"),
                    choices=VOTE_DIRECTIONS,
                    help_text=_("+1 for upvote, -1 for downvote."))
    reason      = models.CharField(_("reason"),
                    max_length=REASON_LENGTH,
                    help_text=_("An adjective describing the item being "
                                "voted for."))

    class Meta:
        ordering = ['content_type', '-direction', 'reason']
        index_together = (
            ("content_type", "direction", "reason"),
        )
        unique_together = ("content_type", "reason")

        verbose_name = "voting reason"
        verbose_name_plural = "voting reasons"

    def __str__(self):
        model_name = self.content_type.model_class()._meta.verbose_name_plural
        if self.reason:
            return ("%s %s for %s" %
                    (self.get_direction_display(), self.reason, model_name))
        else:
            return ("%s for %s" % (self.get_direction_display(), model_name))

    @property
    def description(self):
        if self.reason:
            return "%s %s" % (self.get_direction_display(), self.reason)
        else:
            return self.get_direction_display()


@python_2_unicode_compatible
class AbstractVote(models.Model):
    """
    An individual user's vote on some content item.

    (The precise item is left unspecified in this class.
    Subclasses should have a readable and writable "item" property,
    and establish the "unique" constraint between user and item.)
    """
    CLASSIFIER_LENGTH = 32

    user        = models.ForeignKey(settings.AUTH_USER_MODEL,
                    verbose_name=_("user"),
                    help_text=_("The user who placed this vote. "
                                "(Each user only gets one vote per item.)"))

    direction   = models.SmallIntegerField(_("direction"),
                    choices=VOTE_DIRECTIONS,
                    help_text=_("+1 for upvote, -1 for downvote."))
    reason      = models.CharField(_("reason"),
                    max_length=VoteReason.REASON_LENGTH, blank=True,
                    help_text=_("An explanation of the vote. Valid choices "
                                "are stored as VoteReasons."))

    vote_date   = models.DateTimeField(_("placed at"), default=timezone.now,
                    help_text=_("The date and time at which the vote was "
                                "placed."))

    effective   = models.BooleanField(_("effective"), default=True,
                    help_text=_("If this is false, the vote is not counted, "
                                "but the user still sees it."))
    classifier  = models.CharField(_("classifier"),
                    max_length=CLASSIFIER_LENGTH, blank=True,
                    help_text=_("Metadata storage for moderation or "
                                "antispam systems. You can use this to "
                                "indicate why a vote was marked ineffective."))

    class Meta:
        abstract = True

    def __str__(self):
        if self.reason:
            return ("%s's %s %s to %s" %
                    (self.user, self.get_direction_display(),
                     self.reason, self.item))
        else:
            return ("%s's %s to %s" %
                    (self.user, self.get_direction_display(), self.item))

    def save(self, *args, **kwargs):
        new = self.id is None
        pre_vote.send(self.item, vote=self, new=new)

        with transaction.atomic():
            super(AbstractVote, self).save(*args, **kwargs)
            self.item.votes.update_scores()
            self.item.save()

        post_vote.send(self.item, vote=self, new=new)

    def delete(self, *args, **kwargs):
        pre_remove_vote.send(self.item, vote=self)

        with transaction.atomic():
            super(AbstractVote, self).delete(*args, **kwargs)
            self.item.votes.update_scores()
            self.item.save()

        post_remove_vote.send(self.item, vote=self)


class Vote(AbstractVote):
    """
    An individual user's vote on some content item.

    This is a specialization of AbstractVote that uses a GenericForeignKey
    to select the object.
    """
    objects = VoteManager()

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    item = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = ("user", "content_type", "object_id")
        index_together = (
            ("content_type", "object_id", "effective", "direction"),
        )

