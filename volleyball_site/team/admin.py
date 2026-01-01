from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered
from .models import Player, AccessCode, PlayerProfile, PlayerStats, GameVideo, AISummary


class PlayerAdmin(admin.ModelAdmin):
    list_display = ("number", "first_name", "last_name", "position")
    list_filter = ("position",)
    search_fields = ("first_name", "last_name")


class AccessCodeAdmin(admin.ModelAdmin):
    list_display = ("code", "role", "is_used", "allowed_email", "expires_at", "created_at")
    readonly_fields = ("created_at",)


class PlayerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "player", "position", "height")


class PlayerStatsAdmin(admin.ModelAdmin):
    list_display = ("player", "kills", "blocks", "aces", "digs", "updated_at")


class GameVideoAdmin(admin.ModelAdmin):
    list_display = ("title", "game_date", "opponent", "game_type", "uploaded_by", "view_count", "is_featured", "private", "uploaded_at")
    list_filter = ("game_type", "is_featured", "private", "uploaded_at", "game_date")
    search_fields = ("title", "opponent", "description")
    readonly_fields = ("file_size_mb", "view_count", "uploaded_at", "updated_at")
    fieldsets = (
        ("Video Info", {
            'fields': ('title', 'description', 'video', 'thumbnail')
        }),
        ("Game Details", {
            'fields': ('game_type', 'game_date', 'opponent')
        }),
        ("Metadata", {
            'fields': ('file_size_mb', 'duration_seconds', 'view_count')
        }),
        ("Settings", {
            'fields': ('uploaded_by', 'is_featured', 'private')
        }),
        ("Timestamps", {
            'fields': ('uploaded_at', 'updated_at')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # New object
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)


class AISummaryAdmin(admin.ModelAdmin):
    list_display = ("player", "generated_at")


for model, admin_class in [
    (Player, PlayerAdmin),
    (AccessCode, AccessCodeAdmin),
    (PlayerProfile, PlayerProfileAdmin),
    (PlayerStats, PlayerStatsAdmin),
    (GameVideo, GameVideoAdmin),
    (AISummary, AISummaryAdmin),
]:
    try:
        admin.site.register(model, admin_class)
    except AlreadyRegistered:
        pass
