from django.urls import path
from .views import AthleteCreateView, AthleteMeView

urlpatterns = [
    path("", AthleteCreateView.as_view(), name="athlete-create"),
    path("me/", AthleteMeView.as_view(), name="athlete-me"),
]