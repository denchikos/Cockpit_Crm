import uuid
from django.db import models
from django.utils import timezone
from django.db.models import Q, Func
from django.contrib.postgres.fields import DateTimeRangeField
from django.contrib.postgres.fields import RangeBoundary
from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import RangeOperators


class TsTzRange(Func):
    function = 'TSTZRANGE'
    output_field = DateTimeRangeField()


class EntityType(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def str(self):
        return self.code


class Entity(models.Model):
    entity_uid = models.UUIDField(default=uuid.uuid4, editable=False, db_index=True)
    entity_type = models.ForeignKey(EntityType, on_delete=models.PROTECT, related_name='entities')
    display_name = models.TextField()
    valid_from = models.DateTimeField(default=timezone.now)
    valid_to = models.DateTimeField(null=True, blank=True)
    is_current = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['entity_uid']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['entity_uid'], condition=Q(is_current=True), name='unique_current_entity'),
            ExclusionConstraint(
                name='exclude_overlapping_entity_uid',
                expressions=[
                    (TsTzRange('valid_from', 'valid_to', RangeBoundary()), RangeOperators.OVERLAPS),
                    ('entity_uid', RangeOperators.EQUAL),
                ],
            ),
        ]

    def str(self):
        return f"{self.display_name} ({self.entity_uid})"


class EntityDetail(models.Model):
    entity_uid = models.UUIDField(db_index=True)
    detail_code = models.CharField(max_length=100)
    value = models.JSONField()
    valid_from = models.DateTimeField(default=timezone.now)
    valid_to = models.DateTimeField(null=True, blank=True)
    is_current = models.BooleanField(default=True)
    hashdiff = models.CharField(max_length=128, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['entity_uid', 'detail_code'], condition=Q(is_current=True), name='unique_current_detail'),
            ExclusionConstraint(
                name='exclude_overlapping_detail_per_entity',
                expressions=[
                    (TsTzRange('valid_from', 'valid_to', RangeBoundary()), RangeOperators.OVERLAPS),
                    ('entity_uid', RangeOperators.EQUAL),
                    ('detail_code', RangeOperators.EQUAL),
                ],
            ),
        ]

    def str(self):
        return f"{self.entity_uid} {self.detail_code} -> {self.value}"


class AuditLog(models.Model):
    actor = models.CharField(max_length=200, null=True, blank=True)
    action = models.CharField(max_length=50)
    entity_uid = models.UUIDField(null=True, db_index=True)
    detail_code = models.CharField(max_length=100, null=True, blank=True)
    before = models.JSONField(null=True, blank=True)
    after = models.JSONField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.timestamp} {self.action} {self.entity_uid}"