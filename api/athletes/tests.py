from datetime import date
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import User
from athletes.models import Athlete


class AthleteAPITests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="athleteuser",
            password="test-password",
            first_name="Jane",
            last_name="Doe",
        )
        self.client = APIClient()

    def test_create_athlete_profile_success(self):
        self.client.force_authenticate(user=self.user)
        athlete_data = {
            "date_of_birth": "2002-05-15",
            "gender": Athlete.Gender.FEMALE,
            "country": "Kenya",
            "city": "Nairobi",
            "bio": "Passionate runner",
        }
        response = self.client.post("/api/athletes/", athlete_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Athlete.objects.filter(user=self.user).exists())
        self.assertEqual(response.data["country"], "Kenya")

    def test_create_athlete_profile_duplicate_prevented(self):
        Athlete.objects.create(
            user=self.user,
            date_of_birth=date(2002, 5, 15),
            gender=Athlete.Gender.FEMALE,
            country="Kenya",
            city="Nairobi",
        )
        self.client.force_authenticate(user=self.user)
        athlete_data = {
            "date_of_birth": "2002-05-15",
            "gender": Athlete.Gender.FEMALE,
            "country": "Kenya",
            "city": "Nairobi",
        }
        response = self.client.post("/api/athletes/", athlete_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_athlete_me_profile(self):
        Athlete.objects.create(
            user=self.user,
            date_of_birth=date(2002, 5, 15),
            gender=Athlete.Gender.FEMALE,
            country="Kenya",
            city="Nairobi",
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/athletes/me/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["city"], "Nairobi")

    def test_get_athlete_me_not_found(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/athletes/me/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_athlete_me_profile(self):
        Athlete.objects.create(
            user=self.user,
            date_of_birth=date(2002, 5, 15),
            gender=Athlete.Gender.FEMALE,
            country="Kenya",
            city="Nairobi",
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.patch("/api/athletes/me/", {"city": "Mombasa"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["city"], "Mombasa")
