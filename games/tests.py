from datetime import date, timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from accounts.models import User
from athletes.models import Athlete
from games.models import Game, GameParticipant, GameStat, GameVerification
from sports.models import AthleteSport, Sport, SportPosition, StatType


class GameModelTests(TestCase):
    def setUp(self):
        self.creator = User.objects.create_user(
            username="recorder",
            password="test-password",
        )
        self.scout = User.objects.create_user(
            username="scout",
            password="test-password",
            role=User.Role.SCOUT,
        )
        athlete_user = User.objects.create_user(
            username="amani",
            password="test-password",
        )
        self.athlete = Athlete.objects.create(
            user=athlete_user,
            date_of_birth=date(2008, 5, 12),
            gender=Athlete.Gender.FEMALE,
            country="Kenya",
            city="Nairobi",
        )
        self.football = Sport.objects.create(
            name="Football",
            supports_positions=True,
        )
        self.athletics = Sport.objects.create(name="Athletics")
        self.midfielder = SportPosition.objects.create(
            sport=self.football,
            name="Midfielder",
        )
        self.football_profile = AthleteSport.objects.create(
            athlete=self.athlete,
            sport=self.football,
            primary_position=self.midfielder,
            is_primary=True,
        )
        self.athletics_profile = AthleteSport.objects.create(
            athlete=self.athlete,
            sport=self.athletics,
        )
        self.goals = StatType.objects.create(
            sport=self.football,
            name="Goals",
            key="goals",
        )
        self.sprint_time = StatType.objects.create(
            sport=self.athletics,
            name="100 metre sprint time",
            key="sprint_time_s",
            unit="seconds",
        )
        self.game = Game.objects.create(
            sport=self.football,
            title="Nairobi Youth Cup — Final",
            created_by=self.creator,
            location="Nairobi",
            format="11-a-side",
            started_at=timezone.now(),
        )

    def test_participant_must_use_a_profile_for_the_game_sport(self):
        participant = GameParticipant(
            game=self.game,
            athlete=self.athlete,
            athlete_sport=self.athletics_profile,
        )

        with self.assertRaises(ValidationError):
            participant.full_clean()

    def test_game_stat_accepts_a_matching_participant_and_metric(self):
        participant = GameParticipant.objects.create(
            game=self.game,
            athlete=self.athlete,
            athlete_sport=self.football_profile,
            position=self.midfielder,
            team=GameParticipant.Team.A,
            confirmed=True,
        )

        stat = GameStat.objects.create(
            game=self.game,
            participant=participant,
            stat_type=self.goals,
            value="2",
            recorded_by=self.creator,
        )

        self.assertEqual(stat.period, "full_game")
        self.assertEqual(stat.value, 2)

    def test_game_stat_rejects_a_metric_from_another_sport(self):
        participant = GameParticipant.objects.create(
            game=self.game,
            athlete=self.athlete,
            athlete_sport=self.football_profile,
        )
        stat = GameStat(
            game=self.game,
            participant=participant,
            stat_type=self.sprint_time,
            value="11.25",
        )

        with self.assertRaises(ValidationError):
            stat.full_clean()

    def test_game_stat_rejects_a_participant_from_another_game(self):
        participant = GameParticipant.objects.create(
            game=self.game,
            athlete=self.athlete,
            athlete_sport=self.football_profile,
        )
        other_game = Game.objects.create(
            sport=self.football,
            title="Nairobi Youth Cup — Semi-final",
            created_by=self.creator,
            location="Nairobi",
            format="11-a-side",
        )
        stat = GameStat(
            game=other_game,
            participant=participant,
            stat_type=self.goals,
            value="1",
        )

        with self.assertRaises(ValidationError):
            stat.full_clean()

    def test_verified_game_records_the_verifier_and_time(self):
        verification = GameVerification.objects.create(
            game=self.game,
            method=GameVerification.Method.SCOUT,
            status=GameVerification.Status.VERIFIED,
            verified_by=self.scout,
        )

        self.assertEqual(verification.verified_by, self.scout)
        self.assertIsNotNone(verification.verified_at)

    def test_game_cannot_end_before_it_starts(self):
        game = Game(
            sport=self.football,
            title="Invalid schedule",
            created_by=self.creator,
            location="Nairobi",
            format="11-a-side",
            started_at=timezone.now(),
            ended_at=timezone.now() - timedelta(minutes=10),
        )

        with self.assertRaises(ValidationError):
            game.full_clean()
