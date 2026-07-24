from django.urls import path

from .views import (
    GameListCreateView,
    GameDetailView,
    GameParticipantListCreateView,
    GameParticipantDetailView,
)

urlpatterns = [
    path("", GameListCreateView.as_view()),
    path("<uuid:pk>/", GameDetailView.as_view()),

    path(
    "<uuid:game_id>/participants/",
    GameParticipantListCreateView.as_view(),
    name="game-participant-list",
        ),

    path(
        "participants/<uuid:pk>/",
        GameParticipantDetailView.as_view(),
        name="game-participant-detail",
        ),
]