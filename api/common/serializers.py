from rest_framework import serializers

from athletes.models import Athlete
from sports.models import Sport, SportPosition


class AthleteSummarySerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="user.get_full_name")

    class Meta:
        model = Athlete
        fields = [
            "athlete_id",
            "name",
            "country",
            "profile_photo",
        ]

class SportSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Sport
        fields = [
            "id",
            "name",
        ]


class PositionSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = SportPosition
        fields = [
            "id",
            "name",
        ]