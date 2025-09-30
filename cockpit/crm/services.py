import hashlib
from django.db import transaction
from django.utils import timezone
from .models import Entity, EntityDetail, EntityType, AuditLog


def compute_hashdiff(value: dict) -> str:
    if isinstance(value, dict):
        raw = str(sorted(value.items())).encode('utf-8')
    else:
        raw = str(value).encode('utf-8')
    return hashlib.sha256(raw).hexdigest()


@transaction.atomic
def scd2_upsert_entity(entity_uid, entity_type_code, display_name, actor=None, change_ts=None):
    if change_ts is None:
        change_ts = timezone.now()
    et, _ = EntityType.objects.get_or_create(code=entity_type_code)
    current = Entity.objects.filter(entity_uid=entity_uid, is_current=True).first()

    if current:
        if current.display_name == display_name and current.entity_type == et:
            return current
        current.is_current = False
        current.valid_to = change_ts
        current.save(update_fields=['is_current', 'valid_to', 'updated_at'])

    new_entity = Entity.objects.create(
        entity_uid=entity_uid,
        entity_type=et,
        display_name=display_name,
        valid_from=change_ts,
        is_current=True,
    )

    # лог
    AuditLog.objects.create(
        actor=actor,
        action='UPSERT_ENTITY',
        entity_uid=entity_uid,
        before={'display_name': current.display_name if current else None},
        after={'display_name': display_name},
    )

    return new_entity


@transaction.atomic
def scd2_upsert_detail(entity_uid, detail_code, value, actor=None, change_ts=None):
    if change_ts is None:
        change_ts = timezone.now()

    hashdiff = compute_hashdiff(value)

    current = EntityDetail.objects.filter(
        entity_uid=entity_uid,
        detail_code=detail_code,
        is_current=True
    ).first()

    if current:
        if current.hashdiff == hashdiff:
            return current

        current.is_current = False
        current.valid_to = change_ts
        current.save(update_fields=['is_current', 'valid_to', 'updated_at'])

    new_detail = EntityDetail.objects.create(
        entity_uid=entity_uid,
        detail_code=detail_code,
        value=value,
        hashdiff=hashdiff,
        valid_from=change_ts,
        is_current=True,
    )

    AuditLog.objects.create(
        actor=actor,
        action='UPSERT_DETAIL',
        entity_uid=entity_uid,
        detail_code=detail_code,
        before={'value': current.value if current else None},
        after={'value': value},
    )

    return new_detail
