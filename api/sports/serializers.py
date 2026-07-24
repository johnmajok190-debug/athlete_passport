from rest_framework import serializers

from sports.models import AthleteSport, Sport, SportPosition


class SportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sport
        fields = [
            "id",
            "name",
            "supports_positions",
        ]


class SportReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sport
        fields = ["id", "name"]


class SportPositionReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SportPosition
        fields = ["id", "name"]


class AthleteSportReadSerializer(serializers.ModelSerializer):
    sport = SportReferenceSerializer(read_only=True)
    primary_position = SportPositionReferenceSerializer(read_only=True)

    class Meta:
        model = AthleteSport
        fields = [
            "id",
            "sport",
            "primary_position",
            "is_primary",
            "started_playing",
        ]


class AthleteSportWriteSerializer(serializers.ModelSerializer):
    sport = serializers.PrimaryKeyRelatedField(queryset=Sport.objects.all())
    primary_position = serializers.PrimaryKeyRelatedField(
        queryset=SportPosition.objects.all(),
        allow_null=True,
        required=False,
    )

    class Meta:
        model = AthleteSport
        fields = [
            "id",
            "sport",
            "primary_position",
            "is_primary",
            "started_playing",
        ]
        read_only_fields = ["id"]
