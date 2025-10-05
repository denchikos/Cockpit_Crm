import hashlib
from django.db import transaction, connection
from django.utils import timezone
from crm.models import Entity, EntityDetail, EntityType, AuditLog


def compute_hashdiff(value: dict) -> str:
    if isinstance(value, dict):
        raw = str(sorted(value.items())).encode('utf-8')
    else:
        raw = str(value).encode('utf-8')
    return hashlib.sha256(raw).hexdigest()


@transaction.atomic
def scd2_upsert_entity(entity_uid, entity_type_code, display_name, details=None, actor="system", change_ts=None):
    if change_ts is None:
        change_ts = timezone.now()

    et, _ = EntityType.objects.get_or_create(code=entity_type_code)
    current = Entity.objects.filter(entity_uid=entity_uid, is_current=True).first()

    new_hash = compute_hashdiff({
        "display_name": display_name,
        "entity_type": entity_type_code,
    })

    if not current:
        entity = Entity.objects.create(
            entity_uid=entity_uid,
            entity_type=et,
            display_name=display_name,
            valid_from=change_ts,
            is_current=True,
        )
        AuditLog.objects.create(
            actor=actor,
            action="INSERT_ENTITY",
            entity_uid=entity_uid,
            before=None,
            after={"display_name": display_name, "entity_type": entity_type_code},
        )

    else:
        old_hash = compute_hashdiff({
            "display_name": current.display_name,
            "entity_type": current.entity_type.code,
        })

        if new_hash == old_hash:
            entity = current
        else:
            current.valid_to = change_ts
            current.is_current = False
            current.save(update_fields=["is_current", "valid_to", "updated_at"])

            entity = Entity.objects.create(
                entity_uid=entity_uid,
                entity_type=et,
                display_name=display_name,
                valid_from=change_ts,
                is_current=True,
            )

            AuditLog.objects.create(
                actor=actor,
                action="UPDATE_ENTITY",
                entity_uid=entity_uid,
                before={"display_name": current.display_name},
                after={"display_name": display_name},
            )

    if details:
        for d in details:
            scd2_upsert_detail(
                entity_uid=entity.entity_uid,
                detail_code=d["detail_code"],
                value=d["value"],
                actor=actor,
                change_ts=change_ts,
            )

    return entity


@transaction.atomic
def scd2_upsert_detail(entity_uid, detail_code, value, actor="system", change_ts=None):
    if change_ts is None:
        change_ts = timezone.now()

    business_value = value.get('value') if isinstance(value, dict) and 'value' in value else value
    hashdiff = compute_hashdiff(business_value)
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
        current.save(update_fields=["is_current", "valid_to", "updated_at"])

        action = "UPDATE_DETAIL"
        before_val = current.value

        detail = EntityDetail.objects.create(
            entity_uid=entity_uid,
            detail_code=detail_code,
            value=value,
            hashdiff=hashdiff,
            valid_from=change_ts,
            is_current=True,
        )

        AuditLog.objects.create(
            actor=actor,
            action=action,
            entity_uid=entity_uid,
            detail_code=detail_code,
            before=before_val,
            after=value,
        )

        return detail
    else:
        action = 'INSERT_DETAIL'
        before_val = None

        detail = EntityDetail.objects.create(
            entity_uid=entity_uid,
            detail_code=detail_code,
            value=value,
            hashdiff=hashdiff,
            valid_from=change_ts,
            is_current=True,
        )

        AuditLog.objects.create(
            actor=actor,
            action=action,
            entity_uid=entity_uid,
            detail_code=detail_code,
            before=before_val,
            after=value,
        )

        return detail


def refresh_materialized_views():
    try:
        with connection.cursor() as cursor:
            cursor.execute("REFRESH MATERIALIZED VIEW CONCURRENTLY entity_current_snapshot;")
    except Exception as e:
        print(f'[WARN] Materialized view not found or refresh failed: {e}')