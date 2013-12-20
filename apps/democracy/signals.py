# -*- coding: utf-8 -*-
"""
democracy.signals
=================
Signals for your code to interfere in the democratic process.
(You can use this for antispam, moderation, et cetera.)

:copyright: (C) 2013 Matthew Frazier
:license:   MIT/X11, see package's LICENSE for details
"""
from __future__ import unicode_literals
import django.dispatch

#: Dispatched before a Vote for the sender is saved to the database,
#: including both new votes and altered votes.
#: This runs outside the atomic() block, so you can stop the vote here
#: or make it ineffective.
pre_vote = django.dispatch.Signal(providing_args=["vote", "new"])

#: Dispatched after a Vote for the sender is saved to the database,
#: including both new votes and altered votes.
post_vote = django.dispatch.Signal(providing_args=["vote", "new"])

#: Dispatched before a Vote for the sender is removed from the database.
pre_remove_vote = django.dispatch.Signal(providing_args=["vote"])

#: Dispatched after a Vote for the sender is removed from the database.
post_remove_vote = django.dispatch.Signal(providing_args=["vote"])

