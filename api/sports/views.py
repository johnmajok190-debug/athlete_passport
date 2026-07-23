from rest_framework import generics, permissions
from rest_framework.permissions import AllowAny

from sports.models import Sport, AthleteSport
from .serializers import SportSerializer, AthleteSportSerializer


class SportListView(generics.ListAPIView):
    serializer_class = SportSerializer
    permission_classes = [AllowAny]
    queryset = Sport.objects.filter(is_active=True).order_by("name")

    def get_queryset(self):
        return Sport.objects.filter(is_active=True).order_by("name")


class SportDetailView(generics.RetrieveAPIView):
    serializer_class = SportSerializer
    permission_classes = [AllowAny]
    queryset = Sport.objects.filter(is_active=True)

class AthleteSportCreateView(generics.ListCreateAPIView):
    serializer_class = AthleteSportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return AthleteSport.objects.filter(
            athlete=self.request.user.athlete_profile
        )

    def perform_create(self, serializer):
        serializer.save(
            athlete=self.request.user.athlete_profile
        )