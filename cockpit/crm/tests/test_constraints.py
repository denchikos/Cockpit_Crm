import pytest
from django.db import IntegrityError, transaction
from django.utils import timezone
from crm.models import EntityType, Entity


@pytest.mark.django_db
def test_entity_exclusion_constraint():
    etype = EntityType.objects.create(code='PERSON')

    uid = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'

    Entity.objects.create(
        entity_uid=uid,
        entity_type=etype,
        display_name='Alic',
        valid_from=timezone.now(),
        valid_to=None,
        is_current=True,
    )

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Entity.objects.create(
                entity_uid=uid,
                entity_type=etype,
                display_name='Alic v2',
                valid_from=timezone.now(),
                valid_to=None,
                is_current=True,
            )
