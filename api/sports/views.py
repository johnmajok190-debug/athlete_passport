from rest_framework import generics, permissions, serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from sports.models import Sport, AthleteSport
from .serializers import (
    AthleteSportReadSerializer,
    AthleteSportWriteSerializer,
    SportSerializer,
)


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
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            AthleteSport.objects.filter(
                athlete__user=self.request.user
            )
            .select_related(
                "sport",
                "primary_position",
            )
        )

    def perform_create(self, serializer):
        if not hasattr(self.request.user, "athlete_profile"):
            raise serializers.ValidationError(
                {"detail": "Athlete profile required to register a sport."}
            )
        serializer.save(
            athlete=self.request.user.athlete_profile
        )

    def get_serializer_class(self):
        if self.request.method == "GET":
            return AthleteSportReadSerializer
        return AthleteSportWriteSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        response_serializer = AthleteSportReadSerializer(
            serializer.instance,
            context=self.get_serializer_context(),
        )
        headers = self.get_success_headers(response_serializer.data)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )


class AthleteSportDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            AthleteSport.objects.filter(
                athlete__user=self.request.user
            )
            .select_related("sport", "primary_position")
        )

    def get_serializer_class(self):
        if self.request.method == "GET":
            return AthleteSportReadSerializer
        return AthleteSportWriteSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial,
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}

        response_serializer = AthleteSportReadSerializer(
            serializer.instance,
            context=self.get_serializer_context(),
        )
        return Response(response_serializer.data)
