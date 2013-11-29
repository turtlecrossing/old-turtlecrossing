from django.conf.urls import patterns
from django.conf.urls import url

from .views import FrontPageView, StoryDetailView, SubmitStoryView

urlpatterns = patterns("",
    url(
        regex=r"^$",
        view=FrontPageView.as_view(),
        name="osnap-front-page"
    ),
    url(
        regex=r"^stories/(?P<id>\d+)/$",
        view=StoryDetailView.as_view(),
        name="osnap-story-detail"
    ),
    url(
        regex=r"^stories/submit/$",
        view=SubmitStoryView.as_view(),
        name="osnap-story-submit"
    ),
)

