from rest_framework import generics, permissions

from games.models import GameStat
from .serializers import GameStatSerializer


class GameStatListCreateView(generics.ListCreateAPIView):
    serializer_class = GameStatSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            GameStat.objects.filter(
                participant__athlete__user=self.request.user
            )
            .select_related(
                "game",
                "participant",
                "participant__athlete",
                "participant__athlete__user",
                "stat_type",
                "recorded_by",
            )
        )


class GameStatDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = GameStatSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            GameStat.objects.filter(
                participant__athlete__user=self.request.user
            )
            .select_related(
                "game",
                "participant",
                "participant__athlete",
                "participant__athlete__user",
                "stat_type",
                "recorded_by",
            )
        )