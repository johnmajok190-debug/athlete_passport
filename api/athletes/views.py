from rest_framework import generics, permissions, serializers
from rest_framework.exceptions import NotFound

from athletes.models import Athlete
from .serializers import AthleteSerializer


class AthleteCreateView(generics.CreateAPIView):
    queryset = Athlete.objects.all()
    serializer_class = AthleteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if hasattr(self.request.user, "athlete_profile"):
            raise serializers.ValidationError(
                {"detail": "An athlete profile already exists for this user."}
            )
        serializer.save(user=self.request.user)



class AthleteMeView(generics.RetrieveUpdateAPIView):
    serializer_class = AthleteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        try:
            return self.request.user.athlete_profile
        except Athlete.DoesNotExist:
            raise NotFound("Athlete profile not found.")