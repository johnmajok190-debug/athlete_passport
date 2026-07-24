from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


class AuthenticationAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "StrongPassword123!",
            "password_confirm": "StrongPassword123!",
            "first_name": "Test",
            "last_name": "User",
        }

    def test_register_user_success(self):
        response = self.client.post("/api/auth/register/", self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "Account created successfully.")
        self.assertTrue(User.objects.filter(username="testuser").exists())

    def test_register_user_password_mismatch(self):
        data = self.user_data.copy()
        data["password_confirm"] = "DifferentPassword123!"
        response = self.client.post("/api/auth/register/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password_confirm", response.data)

    def test_login_success(self):
        User.objects.create_user(username="testuser", password="StrongPassword123!")
        login_data = {
            "username": "testuser",
            "password": "StrongPassword123!",
        }
        response = self.client.post("/api/auth/login/", login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_token_refresh(self):
        User.objects.create_user(username="testuser", password="StrongPassword123!")
        login_response = self.client.post(
            "/api/auth/login/",
            {"username": "testuser", "password": "StrongPassword123!"},
            format="json",
        )
        refresh_token = login_response.data["refresh"]
        response = self.client.post(
            "/api/auth/refresh/",
            {"refresh": refresh_token},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
