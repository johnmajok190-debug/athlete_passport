from rest_framework import generics, permissions

from games.models import Game, GameParticipant
from .serializers import GameSerializer, GameParticipantSerializer


class GameListCreateView(generics.ListCreateAPIView):
    serializer_class = GameSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Game.objects.filter(created_by=self.request.user)
            .select_related(
                "sport",
                "format",
                "created_by",
            )
            .order_by("-created_at")
        )

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class GameDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = GameSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Game.objects.filter(created_by=self.request.user)
            .select_related(
                "sport",
                "format",
                "created_by",
            )
        )

class GameParticipantListCreateView(generics.ListCreateAPIView):
    serializer_class = GameParticipantSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            GameParticipant.objects.filter(
                game_id=self.kwargs["game_id"]
            )
            .select_related(
                "athlete",
                "athlete_sport",
                "position",
                "game",
            )
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if "game_id" in self.kwargs:
            game = Game.objects.filter(pk=self.kwargs["game_id"]).first()
            if game:
                context["game"] = game
        return context

    def perform_create(self, serializer):
        game = generics.get_object_or_404(
            Game,
            pk=self.kwargs["game_id"],
        )

        serializer.save(game=game)


class GameParticipantDetailView(
    generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = GameParticipantSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            GameParticipant.objects.select_related(
                "athlete",
                "athlete_sport",
                "position",
                "game",
            )
        )