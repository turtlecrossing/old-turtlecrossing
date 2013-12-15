# -*- coding: utf-8 -*-
"""
osnap.people.models
===================
A custom user model, which includes the limited social functions of OSNAP.

:copyright: (C) 2013 Matthew Frazier
:license:   GNU GPL version 2 or later, see LICENSE for details
"""
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import (AbstractBaseUser, PermissionsMixin,
                                        UserManager)
from django.core import validators
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

class User(AbstractBaseUser, PermissionsMixin):
    """
    A variant of user with additional profile data, which ignores first name
    and last name.

    Username, password and email are required. Other fields are optional.
    """
    objects = UserManager()

    username    = models.CharField(_('username'), max_length=30, unique=True,
                    help_text=_("Your handle on the site. This can be a "
                                "variant of your legal name, or a nickname. "
                                "30 characters or fewer, "
                                "A-Z, a-z, 0-9, and _ only."),
                    validators=[
                        validators.RegexValidator(
                            r'^[a-zA-Z0-9_]+$',
                            _("Enter a valid username."), 'invalid'
                        )
                    ])
    email       = models.EmailField(_('email address'), blank=True)

    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    is_staff    = models.BooleanField(_('staff status'), default=False,
                    help_text=_("Designates whether the user can log "
                                "into this admin site."))
    is_active   = models.BooleanField(_('active'), default=True,
                    help_text=_("Designates whether this user should be "
                                "treated as active. Unselect this "
                                "instead of deleting accounts."))

    full_name   = models.CharField(_('full name'), max_length=30, blank=True,
                    help_text=_("A name by which you are known, which will "
                                "be displayed on your profile. This does "
                                "not have to be your legal name."))
    biography   = models.TextField(_('biography'), blank=True,
                    help_text=_("Additional text about yourself. This is a "
                                "good place to link to your home page or "
                                "projects you work on."))

    gravatar_email = models.EmailField(_('Gravatar email address'), blank=True,
                    help_text=_("This email will be used to look up your "
                                "avatar on gravatar.com. This doesn't have "
                                "to be the same as your normal email, and "
                                "it will not be displayed publicly."))

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        """
        Returns a full name for this user.
        """
        return self.full_name or self.username

    def get_short_name(self):
        """
        Returns a short name for this user.
        """
        return self.username

