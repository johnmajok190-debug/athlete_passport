from django.urls import path

from .views import SportDetailView, SportListView,AthleteSportCreateView

urlpatterns = [
    path("", SportListView.as_view(), name="sport-list"),
    path("<uuid:pk>/", SportDetailView.as_view(), name="sport-detail"),
    path(
        "athlete-sports/",
        AthleteSportCreateView.as_view(),
        name="athlete-sport-list-create",
    ),
]