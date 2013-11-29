"""
osnap.stories.models
====================
Database models! These are fairly simple.

:copyright: (C) 2013 Matthew Frazier
:license:   GNU GPL version 2 or later, see LICENSE for details
"""
from urlparse import urlparse

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

# Create your models here.

@python_2_unicode_compatible
class Story(models.Model):
    """
    Represents a news story - either a link, or a text post (but not both!).
    """
    title       = models.CharField(u"Title", max_length=127,
                    help_text=u"The post's title, which is shown in lists.")

    url         = models.URLField(u"URL", blank=True,
                    help_text=u"The URL of an article to discuss. "
                              u"Mutually exclusive with Text.")

    text        = models.TextField(u"Text", blank=True,
                    help_text=u"The post's content, for standalone posts. "
                              u"Mutually exclusive with URL.")

    submit_date = models.DateTimeField(u"Submitted at", default=timezone.now)

    submitter   = models.ForeignKey(settings.AUTH_USER_MODEL,
                    verbose_name=u"Submitter",
                    blank=True, null=True, on_delete=models.SET_NULL)

    published   = models.BooleanField(u"Published", default=True,
                    help_text=u"Uncheck, and the story disappears from "
                              u"the site.")

    class Meta:
        verbose_name_plural = u"stories"

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
                _(u"A story must include a URL or text."),
                code='neither_type'
            )

        if self.url and self.text:
            raise ValidationError(
                _(u"A story cannot include both a URL and text."),
                code='both_types'
            )

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse('osnap-story-detail', kwargs={'id': self.id})

