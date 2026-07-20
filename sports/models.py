import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


class Sport(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    supports_positions = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class SportPosition(models.Model):
    """A playing position that is valid for one sport."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sport = models.ForeignKey(
        Sport,
        on_delete=models.CASCADE,
        related_name="positions",
    )
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["sport", "name"],
                name="unique_position_name_per_sport",
            )
        ]
        ordering = ["sport__name", "name"]

    def __str__(self):
        return f"{self.sport.name}: {self.name}"


class AthleteSport(models.Model):
    """Connects an athlete profile to a sport they play."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    athlete = models.ForeignKey(
        "athletes.Athlete",
        on_delete=models.CASCADE,
        related_name="sport_profiles",
    )
    sport = models.ForeignKey(
        Sport,
        on_delete=models.PROTECT,
        related_name="athlete_profiles",
    )
    primary_position = models.ForeignKey(
        SportPosition,
        on_delete=models.SET_NULL,
        related_name="athlete_profiles",
        blank=True,
        null=True,
    )
    is_primary = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    started_playing = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["athlete", "sport"],
                name="unique_sport_per_athlete",
            ),
            models.UniqueConstraint(
                fields=["athlete"],
                condition=Q(is_primary=True),
                name="one_primary_sport_per_athlete",
            ),
        ]
        ordering = ["-is_primary", "sport__name"]

    def clean(self):
        super().clean()

        if (
            self.primary_position_id
            and self.sport_id
            and self.primary_position.sport_id != self.sport_id
        ):
            raise ValidationError(
                {
                    "primary_position": (
                        "The selected position must belong to the selected sport."
                    )
                }
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.athlete} — {self.sport}"
