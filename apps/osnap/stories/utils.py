# -*- coding: utf-8 -*-
"""
osnap.stories.utils
===================
Industry-standard `utils.py` file full of random stuff.

:copyright: (C) 2013 Matthew Frazier
:license:   GNU GPL version 2 or later, see LICENSE for details
"""
from __future__ import unicode_literals
from django.utils.decorators import method_decorator

def decorated_view(decorator):
    """
    Decorates the `dispatch` method of a generic view with a
    view-function decorator.
    """
    mdec = method_decorator(decorator)
    def decorate(cls):
        # Search the method resolution order for the actual dispatch method.
        # (After all, the whole point of this decorator is *not* having
        # a dispatch method in the class...)
        dispatch = None
        for parent in cls.__mro__:
            if 'dispatch' in parent.__dict__:
                dispatch = parent.__dict__['dispatch']

        if dispatch is None:
            raise TypeError("%s is missing a dispatch method" % cls.__name__)

        # Python gets rather upset if you try to assign to a slot in
        # cls.__dict__. So, traditional monkey patching.
        cls.dispatch = mdec(dispatch)
        return cls
    return decorate

