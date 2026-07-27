from datetime import date
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import User
from athletes.models import Athlete
from games.models import Game, GameParticipant, GameStat
from sports.models import AthleteSport, Sport, SportFormat, StatType


class GameStatAPITests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="john_majok",
            first_name="John",
            last_name="Majok",
            password="test-password",
        )
        self.athlete = Athlete.objects.create(
            user=self.user,
            date_of_birth=date(2000, 1, 1),
            gender=Athlete.Gender.MALE,
            country="South Sudan",
            city="Juba",
        )
        self.basketball = Sport.objects.create(name="Basketball")
        self.basketball_format = SportFormat.objects.create(
            sport=self.basketball,
            name="5 v 5",
            has_teams=True,
        )
        self.athlete_basketball = AthleteSport.objects.create(
            athlete=self.athlete,
            sport=self.basketball,
        )
        self.game = Game.objects.create(
            sport=self.basketball,
            title="National Championship",
            created_by=self.user,
            location="Juba Arena",
            format=self.basketball_format,
        )
        self.participant = GameParticipant.objects.create(
            game=self.game,
            athlete=self.athlete,
            athlete_sport=self.athlete_basketball,
            team=GameParticipant.Team.A,
            confirmed=True,
        )
        self.points_stat_type = StatType.objects.create(
            sport=self.basketball,
            name="Points",
            key="points",
            unit="count",
            value_type=StatType.ValueType.INTEGER,
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_list_game_stats_nested_format(self):
        stat = GameStat.objects.create(
            game=self.game,
            participant=self.participant,
            stat_type=self.points_stat_type,
            period="full_game",
            value="24",
            recorded_by=self.user,
        )

        response = self.client.get("/api/game-stats/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        stat_data = response.data[0]
        self.assertEqual(stat_data["period"], "full_game")
        self.assertEqual(float(stat_data["value"]), 24.0)

        # Check nested participant dictionary structure
        self.assertIn("participant", stat_data)
        self.assertIsInstance(stat_data["participant"], dict)
        self.assertEqual(stat_data["participant"]["id"], str(self.participant.id))
        self.assertIn("athlete", stat_data["participant"])
        self.assertEqual(
            stat_data["participant"]["athlete"]["athlete_id"], self.athlete.athlete_id
        )
        self.assertEqual(
            stat_data["participant"]["athlete"]["name"], "John Majok"
        )

        # Check nested stat_type dictionary structure
        self.assertIn("stat_type", stat_data)
        self.assertIsInstance(stat_data["stat_type"], dict)
        self.assertEqual(stat_data["stat_type"]["name"], "Points")
        self.assertEqual(stat_data["stat_type"]["unit"], "count")

    def test_create_game_stat_with_ids(self):
        data = {
            "participant_id": str(self.participant.id),
            "stat_type_id": str(self.points_stat_type.id),
            "period": "full_game",
            "value": "24",
        }
        response = self.client.post("/api/game-stats/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        resp_data = response.data
        self.assertEqual(resp_data["participant"]["athlete"]["name"], "John Majok")
        self.assertEqual(resp_data["stat_type"]["name"], "Points")

    def test_create_game_stat_legacy_alias(self):
        data = {
            "participant": str(self.participant.id),
            "stat_type": str(self.points_stat_type.id),
            "period": "full_game",
            "value": "15",
        }
        response = self.client.post("/api/game-stats/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["participant"]["athlete"]["name"], "John Majok")

    def test_cannot_create_stat_for_other_user(self):
        other_user = User.objects.create_user(
            username="other_player",
            password="test-password",
        )
        other_athlete = Athlete.objects.create(
            user=other_user,
            date_of_birth=date(2000, 1, 1),
            gender=Athlete.Gender.MALE,
            country="Kenya",
            city="Nairobi",
        )
        other_athlete_sport = AthleteSport.objects.create(
            athlete=other_athlete,
            sport=self.basketball,
        )
        other_participant = GameParticipant.objects.create(
            game=self.game,
            athlete=other_athlete,
            athlete_sport=other_athlete_sport,
            team=GameParticipant.Team.B,
        )

        data = {
            "participant_id": str(other_participant.id),
            "stat_type_id": str(self.points_stat_type.id),
            "period": "full_game",
            "value": "10",
        }
        response = self.client.post("/api/game-stats/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
