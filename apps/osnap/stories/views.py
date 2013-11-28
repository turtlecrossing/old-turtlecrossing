from django.views.generic import ListView, DetailView

from .models import Story

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

