from rest_framework import serializers

from athletes.models import Athlete
from games.models import GameParticipant
from sports.models import Sport, SportPosition, StatType


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


class StatTypeSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = StatType
        fields = [
            "id",
            "name",
            "key",
            "unit",
            "value_type",
        ]


class GameParticipantSummarySerializer(serializers.ModelSerializer):
    athlete = AthleteSummarySerializer(read_only=True)

    class Meta:
        model = GameParticipant
        fields = [
            "id",
            "athlete",
        ]