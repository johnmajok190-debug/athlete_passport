from rest_framework import serializers

from games.models import GameStat, GameParticipant
from sports.models import StatType

from api.common.serializers import (
    GameParticipantSummarySerializer,
    StatTypeSummarySerializer,
)


class GameStatSerializer(serializers.ModelSerializer):
    participant = GameParticipantSummarySerializer(read_only=True)
    stat_type = StatTypeSummarySerializer(read_only=True)

    participant_id = serializers.PrimaryKeyRelatedField(
        source="participant",
        queryset=GameParticipant.objects.all(),
        write_only=True,
    )

    stat_type_id = serializers.PrimaryKeyRelatedField(
        source="stat_type",
        queryset=StatType.objects.all(),
        write_only=True,
    )

    class Meta:
        model = GameStat
        fields = [
            "id",
            "participant",
            "participant_id",
            "stat_type",
            "stat_type_id",
            "period",
            "value",
            "boolean_value",
            "recorded_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "recorded_by",
            "created_at",
            "updated_at",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get("request")
        if request and request.user.is_authenticated:
            self.fields["participant_id"].queryset = GameParticipant.objects.filter(
                athlete__user=request.user
            )

    def to_internal_value(self, data):
        if isinstance(data, dict):
            data = data.copy()
            if "participant" in data and "participant_id" not in data:
                data["participant_id"] = data.pop("participant")
            if "stat_type" in data and "stat_type_id" not in data:
                data["stat_type_id"] = data.pop("stat_type")
        return super().to_internal_value(data)

    def create(self, validated_data):
        participant = validated_data["participant"]

        validated_data["game"] = participant.game
        validated_data["recorded_by"] = self.context["request"].user

        return super().create(validated_data)

    def validate_participant_id(self, value):
        request = self.context.get("request")

        if request and value.athlete.user != request.user:
            raise serializers.ValidationError(
                "You can only record statistics for your own participation."
            )

        return value

    validate_participant = validate_participant_id