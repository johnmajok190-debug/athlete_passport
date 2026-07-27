from django.urls import include, path

urlpatterns = [
    path("auth/", include("api.authentication.urls")),
    path("athletes/", include("api.athletes.urls")),
    path("sports/", include("api.sports.urls")),
    path("games/", include("api.games.urls")),
    path("game-stats/", include("api.game_stats.urls")),
]