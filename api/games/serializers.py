from rest_framework import serializers

from games.models import Game, GameParticipant
from sports.models import AthleteSport, SportPosition

from api.common.serializers import AthleteSummarySerializer, SportSummarySerializer, PositionSummarySerializer


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = [
            "id",
            "sport",
            "title",
            "location",
            "format",
            "status",
            "started_at",
            "ended_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            "id",
            "status",
            "created_at",
            "updated_at",
        )

    def validate(self, attrs):
        sport = attrs.get("sport") or (self.instance.sport if self.instance else None)
        format_obj = attrs.get("format") or (self.instance.format if self.instance else None)

        if sport and format_obj and format_obj.sport_id != sport.id:
            raise serializers.ValidationError(
                {"format": "The selected format must belong to the game sport."}
            )

        started_at = attrs.get("started_at") or (self.instance.started_at if self.instance else None)
        ended_at = attrs.get("ended_at") or (self.instance.ended_at if self.instance else None)

        if started_at and ended_at and ended_at < started_at:
            raise serializers.ValidationError(
                {"ended_at": "The game cannot end before it starts."}
            )

        return attrs


class GameParticipantSerializer(serializers.ModelSerializer):
    athlete = AthleteSummarySerializer(read_only=True)

    sport = SportSummarySerializer(
        source="athlete_sport.sport",
        read_only=True,
    )

    position = PositionSummarySerializer(read_only=True)

    athlete_sport = serializers.PrimaryKeyRelatedField(
        queryset=AthleteSport.objects.none(),
        write_only=True,
    )

    position_id = serializers.PrimaryKeyRelatedField(
        source="position",
        queryset=SportPosition.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = GameParticipant
        fields = [
            "id",
            "athlete",
            "sport",
            "athlete_sport",
            "position",
            "position_id",
            "team",
            "confirmed",
            "checked_in_at",
        ]

        read_only_fields = [
            "id",
            "confirmed",
            "checked_in_at",
        ]


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get("request")
        if request and request.user.is_authenticated:
            self.fields["athlete_sport"].queryset = AthleteSport.objects.filter(
                athlete__user=request.user
            )

    def validate_athlete_sport(self, value):
        request = self.context.get("request")

        if request and value.athlete.user != request.user:
            raise serializers.ValidationError(
                "You can only add your own athlete sport profile."
            )

        return value

    def validate(self, attrs):
        game = self.context.get("game") or (self.instance.game if self.instance else None)
        athlete_sport = attrs.get("athlete_sport") or (self.instance.athlete_sport if self.instance else None)
        position = attrs.get("position") or (self.instance.position if self.instance else None)
        team = attrs.get("team") if "team" in attrs else (self.instance.team if self.instance else None)

        if game and athlete_sport and athlete_sport.sport_id != game.sport_id:
            raise serializers.ValidationError(
                {"athlete_sport": "This sport profile does not match the game sport."}
            )

        if game and position and position.sport_id != game.sport_id:
            raise serializers.ValidationError(
                {"position": "The position must belong to the game sport."}
            )

        if game and game.format:
            if game.format.has_teams and not team:
                raise serializers.ValidationError(
                    {"team": "Choose the participant's team for this format."}
                )
            if not game.format.has_teams and team:
                raise serializers.ValidationError(
                    {"team": "Individual formats do not use Team A or Team B."}
                )

        return attrs

    def create(self, validated_data):
        athlete_sport = validated_data["athlete_sport"]
        validated_data["athlete"] = athlete_sport.athlete
        return super().create(validated_data)
