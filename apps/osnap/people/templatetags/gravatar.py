# -*- coding: utf-8 -*-
"""
osnap.people.templatetags.gravatar
==================================
A fork of Vincent Driessen's django-gravatar, available at:
<https://github.com/nvie/django-gravatar/blob/cdbc5f1197ff7f507bbe26f130568e73e51c0b27/gravatar/templatetags/gravatar.py>.

We're forking it to use our custom User model and gravatar_email field.
As of this writing, the code was available there under a 3-clause BSD license.

:copyright: (C) 2013 Matthew Frazier
:license:   GNU GPL version 2 or later, see LICENSE for details
"""
from __future__ import unicode_literals
import urllib
from hashlib import md5

from django import template
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils import simplejson

User = get_user_model()

GRAVATAR_URL_PREFIX = getattr(settings, "GRAVATAR_URL_PREFIX",
                                      "http://www.gravatar.com/")
GRAVATAR_DEFAULT_IMAGE = getattr(settings, "GRAVATAR_DEFAULT_IMAGE", "")
GRAVATAR_DEFAULT_RATING = getattr(settings, "GRAVATAR_DEFAULT_RATING", "g")
GRAVATAR_DEFAULT_SIZE = getattr(settings, "GRAVATAR_DEFAULT_SIZE", 80)
GRAVATAR_IMG_CLASS = getattr(settings, "GRAVATAR_IMG_CLASS", "gravatar")

register = template.Library()


def _imgclass_attr():
    if GRAVATAR_IMG_CLASS:
        return ' class="%s"' % (GRAVATAR_IMG_CLASS,)
    return ''


def _wrap_img_tag(url, info, size):
    if info is None:
        return mark_safe(
            '<img src="%s"%s alt="Avatar" height="%s" width="%s"/>' %
            (escape(url), _imgclass_attr(), size, size)
        )
    else:
        return mark_safe(
            '<img src="%s"%s alt="Avatar for %s" height="%s" width="%s"/>' %
            (escape(url), _imgclass_attr(), info, size, size)
        )


def _get_user(user):
    if not isinstance(user, User):
        try:
            user = User.objects.get(username=user)
        except User.DoesNotExist:
            raise Exception("Bad user for gravatar.")
    return user


def _get_gravatar_id(email):
    return md5(email).hexdigest()


@register.simple_tag
def gravatar_for_email(email, size=None, rating=None):
    """
    Generates a Gravatar URL for the given email address.

    Syntax::

        {% gravatar_for_email <email> [size] [rating] %}

    Example::

        {% gravatar_for_email someone@example.com 48 pg %}
    """
    gravatar_url = "%savatar/%s" % (GRAVATAR_URL_PREFIX,
            _get_gravatar_id(email))

    parameters = [p for p in (
        ('d', GRAVATAR_DEFAULT_IMAGE),
        ('s', size or GRAVATAR_DEFAULT_SIZE),
        ('r', rating or GRAVATAR_DEFAULT_RATING),
    ) if p[1]]

    if parameters:
        gravatar_url += '?' + urllib.urlencode(parameters, doseq=True)

    return gravatar_url


@register.simple_tag
def gravatar_for_user(user, size=None, rating=None):
    """
    Generates a Gravatar URL for the given user object or username.

    Syntax::

        {% gravatar_for_user <user> [size] [rating] %}

    Example::

        {% gravatar_for_user request.user 48 pg %}
        {% gravatar_for_user 'jtauber' 48 pg %}
    """
    user = _get_user(user)
    return gravatar_for_email(user.gravatar_email or user.email, size, rating)


@register.simple_tag
def gravatar_img_for_email(email, size=None, rating=None):
    """
    Generates a Gravatar img for the given email address.

    Syntax::

        {% gravatar_img_for_email <email> [size] [rating] %}

    Example::

        {% gravatar_img_for_email someone@example.com 48 pg %}
    """
    gravatar_url = gravatar_for_email(email, size, rating)
    return _wrap_img_tag(gravatar_url, email, size)


@register.simple_tag
def gravatar_img_for_user(user, size=None, rating=None):
    """
    Generates a Gravatar img for the given user object or username.

    Syntax::

        {% gravatar_img_for_user <user> [size] [rating] %}

    Example::

        {% gravatar_img_for_user request.user 48 pg %}
        {% gravatar_img_for_user 'jtauber' 48 pg %}
    """
    gravatar_url = gravatar_for_user(user, size, rating)
    return _wrap_img_tag(gravatar_url, user.username, size)

