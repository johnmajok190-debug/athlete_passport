from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase

from accounts.models import User
from athletes.models import Athlete
from sports.models import AthleteSport, Sport, SportFormat, SportPosition, StatType


class AthleteSportModelTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(username="amani", password="test-password")
        self.athlete = Athlete.objects.create(
            user=user,
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

    def test_athlete_can_add_sports_and_choose_a_primary_one(self):
        athlete_sport = AthleteSport.objects.create(
            athlete=self.athlete,
            sport=self.football,
            primary_position=self.midfielder,
            is_primary=True,
        )
        AthleteSport.objects.create(athlete=self.athlete, sport=self.athletics)

        self.assertEqual(self.athlete.sport_profiles.count(), 2)
        self.assertEqual(athlete_sport.primary_position, self.midfielder)

    def test_position_must_belong_to_the_selected_sport(self):
        athlete_sport = AthleteSport(
            athlete=self.athlete,
            sport=self.athletics,
            primary_position=self.midfielder,
        )

        with self.assertRaises(ValidationError):
            athlete_sport.full_clean()

    def test_athlete_can_have_only_one_primary_sport(self):
        AthleteSport.objects.create(
            athlete=self.athlete,
            sport=self.football,
            is_primary=True,
        )

        with self.assertRaises(ValidationError):
            AthleteSport.objects.create(
                athlete=self.athlete,
                sport=self.athletics,
                is_primary=True,
            )

    def test_stat_type_requires_a_unique_key_for_each_sport(self):
        StatType.objects.create(
            sport=self.football,
            name="Goals",
            key="goals",
            short_name="G",
        )
        duplicate = StatType(
            sport=self.football,
            name="Goals scored",
            key="goals",
        )

        with self.assertRaises(ValidationError):
            duplicate.full_clean()

    def test_sport_format_rejects_an_invalid_player_range(self):
        sport_format = SportFormat(
            sport=self.football,
            name="Invalid format",
            min_players_per_side=11,
            max_players_per_side=7,
        )

        with self.assertRaises(ValidationError):
            sport_format.full_clean()
