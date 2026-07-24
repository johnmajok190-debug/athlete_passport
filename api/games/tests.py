from datetime import date, timedelta
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import User
from athletes.models import Athlete
from games.models import Game, GameParticipant
from sports.models import AthleteSport, Sport, SportFormat, SportPosition


class GamesAPITests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="gamecreator",
            password="test-password",
        )
        self.athlete = Athlete.objects.create(
            user=self.user,
            date_of_birth=date(2000, 1, 1),
            gender=Athlete.Gender.MALE,
            country="Kenya",
            city="Nairobi",
        )
        self.football = Sport.objects.create(name="Football", supports_positions=True)
        self.basketball = Sport.objects.create(name="Basketball", supports_positions=True)

        self.midfielder = SportPosition.objects.create(sport=self.football, name="Midfielder")
        self.point_guard = SportPosition.objects.create(sport=self.basketball, name="Point Guard")

        self.football_format = SportFormat.objects.create(
            sport=self.football,
            name="11-a-side",
            has_teams=True,
        )
        self.basketball_format = SportFormat.objects.create(
            sport=self.basketball,
            name="1 v 1",
            has_teams=False,
        )

        self.athlete_football = AthleteSport.objects.create(
            athlete=self.athlete,
            sport=self.football,
            primary_position=self.midfielder,
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_game_success(self):
        data = {
            "title": "Nairobi Youth League",
            "sport": str(self.football.id),
            "format": str(self.football_format.id),
            "location": "City Stadium",
        }
        response = self.client.post("/api/games/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Nairobi Youth League")

    def test_create_game_invalid_format_for_sport(self):
        data = {
            "title": "Invalid Game",
            "sport": str(self.football.id),
            "format": str(self.basketball_format.id),  # Belongs to Basketball, not Football
            "location": "City Stadium",
        }
        response = self.client.post("/api/games/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("format", response.data)

    def test_create_game_invalid_times(self):
        now = timezone.now()
        data = {
            "title": "Time Travel Game",
            "sport": str(self.football.id),
            "format": str(self.football_format.id),
            "location": "City Stadium",
            "started_at": now.isoformat(),
            "ended_at": (now - timedelta(hours=1)).isoformat(),
        }
        response = self.client.post("/api/games/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("ended_at", response.data)

    def test_list_and_get_game_details(self):
        game = Game.objects.create(
            sport=self.football,
            title="Derby Match",
            created_by=self.user,
            location="Stadium A",
            format=self.football_format,
        )
        response = self.client.get("/api/games/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        detail_response = self.client.get(f"/api/games/{game.id}/")
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_response.data["title"], "Derby Match")

    def test_add_game_participant_success(self):
        game = Game.objects.create(
            sport=self.football,
            title="Derby Match",
            created_by=self.user,
            location="Stadium A",
            format=self.football_format,
        )
        participant_data = {
            "athlete_sport": str(self.athlete_football.id),
            "position": str(self.midfielder.id),
            "team": "A",
        }
        response = self.client.post(
            f"/api/games/{game.id}/participants/",
            participant_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["team"], "A")

    def test_add_game_participant_wrong_sport_profile(self):
        basketball_game = Game.objects.create(
            sport=self.basketball,
            title="Hoops 1v1",
            created_by=self.user,
            location="Gym B",
            format=self.basketball_format,
        )
        # Attempt to use football profile for basketball game
        participant_data = {
            "athlete_sport": str(self.athlete_football.id),
        }
        response = self.client.post(
            f"/api/games/{basketball_game.id}/participants/",
            participant_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("athlete_sport", response.data)
