from datetime import date

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import User
from athletes.models import Athlete
from api.sports.serializers import (
    AthleteSportReadSerializer,
    AthleteSportWriteSerializer,
)
from sports.models import AthleteSport, Sport, SportPosition


class AthleteSportSerializerTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(username="amani", password="test-password")
        self.athlete = Athlete.objects.create(
            user=user,
            date_of_birth=date(2008, 5, 12),
            gender=Athlete.Gender.FEMALE,
            country="Kenya",
            city="Nairobi",
        )
        self.basketball = Sport.objects.create(
            name="Basketball",
            supports_positions=True,
        )
        self.football = Sport.objects.create(
            name="Football",
            supports_positions=True,
        )
        self.point_guard = SportPosition.objects.create(
            sport=self.basketball,
            name="Point Guard",
        )
        self.midfielder = SportPosition.objects.create(
            sport=self.football,
            name="Midfielder",
        )

    def test_represents_sport_and_primary_position_with_ids_and_names(self):
        athlete_sport = AthleteSport.objects.create(
            athlete=self.athlete,
            sport=self.basketball,
            primary_position=self.point_guard,
            is_primary=True,
            started_playing=date(2026, 7, 20),
        )

        data = AthleteSportReadSerializer(athlete_sport).data

        self.assertEqual(
            data,
            {
                "id": str(athlete_sport.id),
                "sport": {
                    "id": str(self.basketball.id),
                    "name": "Basketball",
                },
                "primary_position": {
                    "id": str(self.point_guard.id),
                    "name": "Point Guard",
                },
                "is_primary": True,
                "started_playing": "2026-07-20",
            },
        )

    def test_accepts_uuid_values_for_sport_and_primary_position(self):
        serializer = AthleteSportWriteSerializer(
            data={
                "sport": str(self.basketball.id),
                "primary_position": str(self.point_guard.id),
                "is_primary": True,
                "started_playing": "2026-07-20",
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["sport"], self.basketball)
        self.assertEqual(serializer.validated_data["primary_position"], self.point_guard)

    def test_rejects_position_from_different_sport(self):
        serializer = AthleteSportWriteSerializer(
            data={
                "sport": str(self.basketball.id),
                "primary_position": str(self.midfielder.id),
                "is_primary": True,
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("primary_position", serializer.errors)

    def test_create_endpoint_returns_named_sport_and_position_references(self):
        client = APIClient()
        client.force_authenticate(user=self.athlete.user)

        response = client.post(
            "/api/sports/athlete-sports/",
            {
                "sport": str(self.basketball.id),
                "primary_position": str(self.point_guard.id),
                "is_primary": True,
                "started_playing": "2026-07-20",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data["sport"],
            {"id": str(self.basketball.id), "name": "Basketball"},
        )
        self.assertEqual(
            response.data["primary_position"],
            {"id": str(self.point_guard.id), "name": "Point Guard"},
        )

    def test_create_endpoint_user_without_profile_returns_400(self):
        user_no_profile = User.objects.create_user(username="noprofile", password="test-password")
        client = APIClient()
        client.force_authenticate(user=user_no_profile)

        response = client.post(
            "/api/sports/athlete-sports/",
            {
                "sport": str(self.basketball.id),
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_endpoint_returns_named_sport_and_position_references(self):
        athlete_sport = AthleteSport.objects.create(
            athlete=self.athlete,
            sport=self.basketball,
            primary_position=self.point_guard,
            is_primary=True,
        )
        client = APIClient()
        client.force_authenticate(user=self.athlete.user)

        response = client.patch(
            f"/api/sports/athlete-sports/{athlete_sport.id}/",
            {"is_primary": False},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_primary"])
        self.assertEqual(
            response.data["sport"],
            {"id": str(self.basketball.id), "name": "Basketball"},
        )
        self.assertEqual(
            response.data["primary_position"],
            {"id": str(self.point_guard.id), "name": "Point Guard"},
        )

    def test_list_and_detail_sports(self):
        client = APIClient()
        response = client.get("/api/sports/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)

        response_detail = client.get(f"/api/sports/{self.basketball.id}/")
        self.assertEqual(response_detail.status_code, status.HTTP_200_OK)
        self.assertEqual(response_detail.data["name"], "Basketball")
