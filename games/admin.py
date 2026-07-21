from django.contrib import admin

from games.models import Game, GameParticipant, GameStat, GameVerification


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ("title", "sport", "location", "format", "status", "started_at")
    list_filter = ("sport", "status")
    search_fields = ("title", "location", "format__name")


@admin.register(GameParticipant)
class GameParticipantAdmin(admin.ModelAdmin):
    list_display = ("athlete", "game", "team", "position", "confirmed")
    list_filter = ("team", "confirmed", "game__sport")
    search_fields = ("athlete__athlete_id", "athlete__user__username", "game__title")


@admin.register(GameStat)
class GameStatAdmin(admin.ModelAdmin):
    list_display = (
        "participant",
        "stat_type",
        "value",
        "boolean_value",
        "period",
        "game",
    )
    list_filter = ("game__sport", "stat_type", "period")
    search_fields = ("participant__athlete__athlete_id", "stat_type__name", "game__title")


@admin.register(GameVerification)
class GameVerificationAdmin(admin.ModelAdmin):
    list_display = ("game", "method", "status", "verified_by", "verified_at")
    list_filter = ("method", "status")
    search_fields = ("game__title", "verified_by__username")
