from django.urls import path

from .views import (
    GameStatListCreateView,
    GameStatDetailView,
)

urlpatterns = [
    path(
        "",
        GameStatListCreateView.as_view(),
        name="game-stat-list",
    ),
    path(
        "<uuid:pk>/",
        GameStatDetailView.as_view(),
        name="game-stat-detail",
    ),
]