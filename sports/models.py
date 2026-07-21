import uuid

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Q


class Sport(models.Model):
    """A sport available on the athlete passport platform."""

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


class StatType(models.Model):
    """A sport-specific performance metric, such as goals or sprint_time_s."""

    class ValueType(models.TextChoices):
        INTEGER = "INTEGER", "Integer"
        DECIMAL = "DECIMAL", "Decimal"
        BOOLEAN = "BOOLEAN", "Boolean"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sport = models.ForeignKey(
        Sport,
        on_delete=models.CASCADE,
        related_name="stat_types",
    )
    name = models.CharField(max_length=100)
    key = models.CharField(
        max_length=60,
        validators=[
            RegexValidator(
                regex=r"^[a-z][a-z0-9_]*$",
                message="Use lowercase letters, numbers, and underscores only.",
            )
        ],
        help_text="Stable API key, for example goals or sprint_time_s.",
    )
    short_name = models.CharField(max_length=20, null=True, blank=True)
    unit = models.CharField(
        max_length=30,
        default="count",
        blank=True,
        help_text="For example count, metres, seconds, or percent.",
    )
    value_type = models.CharField(
        max_length=20,
        choices=ValueType.choices,
        default=ValueType.INTEGER,
    )
    display_order = models.PositiveSmallIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["sport", "name"],
                name="unique_stat_name_per_sport",
            ),
            models.UniqueConstraint(
                fields=["sport", "key"],
                name="unique_stat_key_per_sport",
            ),
            models.UniqueConstraint(
                fields=["sport", "short_name"],
                name="unique_stat_short_name_per_sport",
            ),
        ]
        ordering = ["sport__name", "display_order", "name"]

    def __str__(self):
        return f"{self.sport.name}: {self.name}"


class SportFormat(models.Model):
    """The competition format for a sport, such as 11-a-side or 100 metres."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sport = models.ForeignKey(
        Sport,
        on_delete=models.CASCADE,
        related_name="formats",
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    min_players_per_side = models.PositiveSmallIntegerField(default=1)
    max_players_per_side = models.PositiveSmallIntegerField(default=1)
    has_teams = models.BooleanField(
        default=True,
        help_text="False for individual events such as athletics or tennis singles.",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sport__name", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["sport", "name"],
                name="unique_format_name_per_sport",
            )
        ]

    def clean(self):
        super().clean()

        if self.min_players_per_side > self.max_players_per_side:
            raise ValidationError(
                {
                    "min_players_per_side": (
                        "Minimum players cannot exceed maximum players."
                    )
                }
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

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
        return f"{self.athlete} - {self.sport}"
