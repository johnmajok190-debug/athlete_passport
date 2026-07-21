import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Game(models.Model):

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        CHECK_IN_OPEN = "CHECK_IN_OPEN", "Check-in Open"
        READY = "READY", "Ready"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        AWAITING_CONFIRMATION = (
            "AWAITING_CONFIRMATION",
            "Awaiting Confirmation",
        )
        VERIFIED = "VERIFIED", "Verified"
        DISPUTED = "DISPUTED", "Disputed"
        CANCELLED = "CANCELLED", "Cancelled"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    sport = models.ForeignKey(
        "sports.Sport",
        on_delete=models.PROTECT,
        related_name="games",
    )

    title = models.CharField(
        max_length=200,
        help_text="For example, Nairobi Youth Cup — Final.",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_games",
    )

    location = models.CharField(
        max_length=255,
    )

    format = models.CharField(
        max_length=50,
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    ended_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def clean(self):
        super().clean()

        if self.started_at and self.ended_at and self.ended_at < self.started_at:
            raise ValidationError(
                {"ended_at": "The game cannot end before it starts."}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.status})"

import uuid

from django.db import models


class GameParticipant(models.Model):

    class Team(models.TextChoices):
        A = "A", "Team A"
        B = "B", "Team B"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    game = models.ForeignKey(
        "games.Game",
        on_delete=models.CASCADE,
        related_name="participants",
    )

    athlete = models.ForeignKey(
        "athletes.Athlete",
        on_delete=models.PROTECT,
        related_name="game_participations",
    )

    athlete_sport = models.ForeignKey(
        "sports.AthleteSport",
        on_delete=models.PROTECT,
        related_name="game_participations",
    )

    position = models.ForeignKey(
        "sports.SportPosition",
        on_delete=models.SET_NULL,
        related_name="game_participations",
        null=True,
        blank=True,
    )

    team = models.CharField(
        max_length=1,
        choices=Team.choices,
        null=True,
        blank=True,
    )

    checked_in_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    confirmed = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["game", "athlete"],
                name="unique_athlete_per_game",
            )
        ]

    def clean(self):
        super().clean()

        if not (self.game_id and self.athlete_id and self.athlete_sport_id):
            return

        if self.athlete_sport.athlete_id != self.athlete_id:
            raise ValidationError(
                {"athlete_sport": "This sport profile belongs to another athlete."}
            )

        if self.athlete_sport.sport_id != self.game.sport_id:
            raise ValidationError(
                {"athlete_sport": "This sport profile does not match the game sport."}
            )

        if self.position_id and self.position.sport_id != self.game.sport_id:
            raise ValidationError(
                {"position": "The position must belong to the game sport."}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.athlete} - {self.game}"
    
class GameVerification(models.Model):

    class Method(models.TextChoices):
        SELF = "SELF", "Self Confirmation"
        INDEPENDENT_RECORDER = "INDEPENDENT_RECORDER", "Independent Recorder"
        COACH = "COACH", "Coach Verified"
        SCOUT = "SCOUT", "Scout Verified"
        OFFICIAL = "OFFICIAL", "Official Event"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        VERIFIED = "VERIFIED", "Verified"
        DISPUTED = "DISPUTED", "Disputed"
        FAILED = "FAILED", "Failed"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    game = models.OneToOneField(
        "games.Game",
        on_delete=models.CASCADE,
        related_name="verification",
    )

    method = models.CharField(
        max_length=40,
        choices=Method.choices,
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING,
    )

    verified_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="game_verifications",
        null=True,
        blank=True,
    )

    evidence_url = models.URLField(blank=True)

    review_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"{self.game} - {self.method}"

    def clean(self):
        super().clean()

        if self.status == self.Status.VERIFIED and not self.verified_by_id:
            raise ValidationError(
                {"verified_by": "Record the person who verified this game."}
            )

    def save(self, *args, **kwargs):
        if self.status == self.Status.VERIFIED and not self.verified_at:
            self.verified_at = timezone.now()
        self.full_clean()
        return super().save(*args, **kwargs)


class GameStat(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    game = models.ForeignKey(
        "games.Game",
        on_delete=models.CASCADE,
        related_name="stats",
    )

    participant = models.ForeignKey(
        "games.GameParticipant",
        on_delete=models.CASCADE,
        related_name="stats",
    )

    stat_type = models.ForeignKey(
        "sports.StatType",
        on_delete=models.PROTECT,
        related_name="game_stats",
    )

    period = models.CharField(
        max_length=50,
        default="full_game",
        help_text="For example full_game, first_half, q1, or set_1.",
    )

    value = models.DecimalField(
        max_digits=12,
        decimal_places=3,
    )

    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="recorded_game_stats",
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["participant", "stat_type", "period"],
                name="unique_stat_per_participant_period",
            )
        ]

    def clean(self):
        super().clean()

        if not (self.participant_id and self.game_id and self.stat_type_id):
            return

        if self.participant.game_id != self.game_id:
            raise ValidationError(
                {"participant": "The participant does not belong to this game."}
            )

        if self.stat_type.sport_id != self.game.sport_id:
            raise ValidationError(
                {"stat_type": "The selected stat type does not belong to this game's sport."}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.participant.athlete} "
            f"- {self.stat_type.name}: {self.value}"
        )
