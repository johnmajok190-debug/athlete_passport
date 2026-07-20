from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ATHLETE = "ATHLETE", "Athlete"
        SCOUT = "SCOUT", "Scout"
        GUARDIAN = "GUARDIAN", "Guardian"
        ADMIN = "ADMIN", "Admin"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.ATHLETE,
    )

    def __str__(self):
        return self.username
