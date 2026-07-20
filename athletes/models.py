import uuid
from django.conf import settings
from django.db import models


def generate_athlete_id():
    """Return a short, public-facing identifier for an athlete profile."""
    return f"ATH-{uuid.uuid4().hex[:8].upper()}"


class Athlete(models.Model):

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        INACTIVE = "INACTIVE", "Inactive"
        SUSPENDED = "SUSPENDED", "Suspended"
        RETIRED = "RETIRED", "Retired"

    class Gender(models.TextChoices):
        MALE = "MALE", "Male"
        FEMALE = "FEMALE", "Female"
        OTHER = "OTHER", "Other"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    athlete_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        default=generate_athlete_id,
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="athlete_profile",
    )

    date_of_birth = models.DateField()

    gender = models.CharField(
        max_length=10,
        choices=Gender.choices,
    )

    height_cm = models.PositiveSmallIntegerField(null=True, blank=True)

    weight_kg = models.PositiveSmallIntegerField(null=True, blank=True)

    country = models.CharField(max_length=100, db_index=True)
    county_or_state = models.CharField(max_length=100, null=True, blank=True)

    city = models.CharField(max_length=100, db_index=True)

    profile_photo = models.ImageField(
        upload_to="athletes/photos/",
        blank=True,
        null=True,
    )

    bio = models.TextField(
        blank=True,
        max_length=500
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return self.user.get_full_name() or self.user.username
