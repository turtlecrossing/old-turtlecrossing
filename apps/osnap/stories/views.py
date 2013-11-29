"""
osnap.stories.views
===================
Views for working with stories directly. (All class-based, of course.)

:copyright: (C) 2013 Matthew Frazier
:license:   GNU GPL version 2 or later, see LICENSE for details
"""
from django.http import HttpResponseRedirect
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .forms import StorySubmitForm
from .models import Story
from .utils import decorated_view

# Create your views here.

class FrontPageView(ListView):
    model = Story
    queryset = Story.objects.filter(published=True)

    template_name = "osnap/front-page.html"
    context_object_name = "stories"


class StoryDetailView(DetailView):
    model = Story
    queryset = Story.objects.filter(published=True)

    pk_url_kwarg = 'id'

    template_name = "osnap/stories/detail.html"
    context_object_name = "story"


@decorated_view(login_required)
class SubmitStoryView(CreateView):
    model = Story
    form_class = StorySubmitForm

    template_name = "osnap/stories/submit.html"
    context_object_name = "story"

    def form_valid(self, form):
        story = form.save(commit=False)
        dupe = Story.objects.find_duplicate_link(story)

        if dupe:
            messages.info(self.request,
                _(u"This story was submitted recently by another user.")
            )
            return HttpResponseRedirect(dupe.get_absolute_url())
        else:
            story.submitter = self.request.user
            story.save()
            return HttpResponseRedirect(story.get_absolute_url())

