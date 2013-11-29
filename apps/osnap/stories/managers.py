"""
osnap.stories.managers
======================
Managers that handle advanced database-related functionality.

:copyright: (C) 2013 Matthew Frazier
:license:   GNU GPL version 2 or later, see LICENSE for details
"""
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

class StoryManager(models.Manager):
    def find_duplicate_link(self, story_draft, hours=None):
        """
        Searches the database for stories with the same URL
        (though the logic may be refined in the future) submitted recently.

        This is not intended to protect against users hitting Submit twice,
        but against multiple users submitting the same link simultaneously.

        :param story_draft: A `Story` object to search for a duplicate of.
        :param hours:       The number of hours back to search for dupes.
                            If `None`, the `OSNAP_DUPLICATE_FILTER_HOURS`
                            setting is consulted, with 0 meaning
                            "don't filter duplicates, just return `None`".

        :return: The earliest duplicate of the story within the hours setting.
        """
        if story_draft.url:
            qs = self.filter(url=story_draft.url)

            if hours is None:
                hours = getattr(settings, 'OSNAP_DUPLICATE_FILTER_HOURS', 0)

            if hours:
                cutoff = timezone.now() - timedelta(hours=hours)
                dupes = self.filter(url=story_draft.url,
                                    submit_date__gte=cutoff) \
                            .order_by('submit_date')[:1]

                if len(dupes):
                    return dupes[0]

        return None

