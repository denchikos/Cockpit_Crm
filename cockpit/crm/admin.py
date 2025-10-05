from django.contrib import admin
from .models import EntityType, Entity, EntityDetail, AuditLog


@admin.register(EntityType)
class EntityTypeAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "description", "created_at")
    search_fields = ("code", "name")


@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    list_display = ("entity_uid", "entity_type", "display_name", "is_current", "valid_from", "valid_to")
    list_filter = ("entity_type", "is_current")
    search_fields = ("display_name", "entity_uid")


@admin.register(EntityDetail)
class EntityDetailAdmin(admin.ModelAdmin):
    list_display = ("entity_uid", "detail_code", "is_current", "valid_from", "valid_to")
    search_fields = ("entity_uid", "detail_code")
    list_filter = ("is_current",)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("actor", "action", "entity_uid", "detail_code", "timestamp")
    list_filter = ("action", "timestamp")
    search_fields = ("entity_uid", "detail_code")