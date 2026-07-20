from django.test import TestCase

from accounts.models import User
from athletes.models import Athlete


class AthleteModelTests(TestCase):
    def test_new_athlete_receives_a_public_id(self):
        user = User.objects.create_user(
            username="ada",
            password="test-password",
            first_name="Ada",
            last_name="Lovelace",
        )

        athlete = Athlete.objects.create(
            user=user,
            date_of_birth="2000-12-10",
            gender=Athlete.Gender.FEMALE,
            country="Kenya",
            city="Nairobi",
        )

        self.assertTrue(athlete.athlete_id.startswith("ATH-"))
        self.assertEqual(str(athlete), "Ada Lovelace")
