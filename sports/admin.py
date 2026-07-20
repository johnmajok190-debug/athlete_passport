from django.contrib import admin

from sports.models import AthleteSport, Sport, SportPosition


@admin.register(Sport)
class SportAdmin(admin.ModelAdmin):
    list_display = ("name", "supports_positions", "is_active")
    list_filter = ("supports_positions", "is_active")
    search_fields = ("name",)


@admin.register(SportPosition)
class SportPositionAdmin(admin.ModelAdmin):
    list_display = ("name", "sport", "is_active")
    list_filter = ("sport", "is_active")
    search_fields = ("name", "sport__name")


@admin.register(AthleteSport)
class AthleteSportAdmin(admin.ModelAdmin):
    list_display = (
        "athlete",
        "sport",
        "primary_position",
        "is_primary",
        "is_active",
    )
    list_filter = ("sport", "is_primary", "is_active")
    search_fields = ("athlete__user__username", "athlete__athlete_id")
