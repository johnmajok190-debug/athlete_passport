from rest_framework import serializers
from athletes.models import Athlete


class AthleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Athlete
        fields = [
            "athlete_id",
            "date_of_birth",
            "gender",
            "height_cm",
            "weight_kg",
            "country",
            "county_or_state",
            "city",
            "profile_photo",
            "bio",
            "status",
        ]

        read_only_fields = [
            "athlete_id",
            "status",
        ]