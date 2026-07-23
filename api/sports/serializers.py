from rest_framework import serializers

from sports.models import Sport, AthleteSport


class SportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sport
        fields = [
            "id",
            "name",
            "supports_positions",
        ]

class AthleteSportSerializer(serializers.ModelSerializer):
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