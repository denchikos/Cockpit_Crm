import uuid
import pytest
from crm.services import scd2_upsert_entity, scd2_upsert_detail
from crm.models import Entity, EntityDetail


@pytest.mark.django_db
def test_entity_upsert_idempotent():
    uid = uuid.uuid4()
    e1 = scd2_upsert_entity(uid, 'PERSON', 'Alic')
    assert e1.is_current is True
    assert Entity.objects.count() == 1
    e2 = scd2_upsert_entity(uid, 'PERSON', 'Alic')
    assert Entity.objects.count() == 1
    assert e1.id == e2.id
    e3 = scd2_upsert_entity(uid, 'PERSON', 'Alic B')
    assert Entity.objects.count() == 2
    e1.refresh_from_db()
    assert not e1.is_current
    assert e3.is_current


@pytest.mark.django_db
def test_detail_upsert_idempotent():
    uid = uuid.uuid4()
    scd2_upsert_entity(uid, 'PERSON', 'Bogdan')
    d1 = scd2_upsert_detail(uid, 'EMAIL', {'value': "bogdan@example.com"})
    assert d1.is_current
    assert EntityDetail.objects.count() == 1
    d2 = scd2_upsert_detail(uid, 'EMAIL', {'value': "bogdan@example.com"})
    assert EntityDetail.objects.count() == 1
    assert d1.id == d2.id
    d3 = scd2_upsert_detail(uid, 'EMAIL', {'value': "bogdan.new@example.com"})
    assert EntityDetail.objects.count() == 2
    d1.refresh_from_db()
    assert not d1.is_current
    assert d3.is_current
