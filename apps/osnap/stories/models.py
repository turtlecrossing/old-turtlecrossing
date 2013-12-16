# -*- coding: utf-8 -*-
"""
osnap.stories.models
====================
Database models! These are fairly simple.

:copyright: (C) 2013 Matthew Frazier
:license:   GNU GPL version 2 or later, see LICENSE for details
"""
from __future__ import unicode_literals
from urlparse import urlparse

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from .managers import StoryManager

@python_2_unicode_compatible
class Story(models.Model):
    """
    Represents a news story - either a link, or a text post (but not both!).
    """
    objects = StoryManager()

    title       = models.CharField(_("title"), max_length=127,
                    help_text=_("the post's title, which is shown in lists."))

    url         = models.URLField(_("URL"), blank=True,
                    help_text=_("The URL of an article to discuss. "
                                "Mutually exclusive with Text."))

    text        = models.TextField(_("text"), blank=True,
                    help_text=_("The post's content, for standalone posts. "
                                "Mutually exclusive with URL."))

    submit_date = models.DateTimeField(_("submitted at"), default=timezone.now)

    submitter   = models.ForeignKey(settings.AUTH_USER_MODEL,
                    verbose_name=_("submitter"),
                    blank=True, null=True, on_delete=models.SET_NULL)

    published   = models.BooleanField(_("published"), default=True,
                    help_text=_("Uncheck, and the story disappears from "
                                "the site."))

    class Meta:
        verbose_name = _("story")
        verbose_name_plural = _("stories")

        get_latest_by = "submit_date"
        ordering = ('-submit_date',)

    def __str__(self):
        return self.title

    @property
    def domain(self):
        return urlparse(self.url).netloc if self.url else ''

    def clean(self):
        # This means, "if there are both or neither."
        if not (self.url or self.text):
            raise ValidationError(
                _("A story must include a URL or text."),
                code='neither_type'
            )

        if self.url and self.text:
            raise ValidationError(
                _("A story cannot include both a URL and text."),
                code='both_types'
            )

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse('osnap_story_detail', kwargs={'id': self.id})

