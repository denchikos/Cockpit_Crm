import uuid
import pytest
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from crm.models import Entity, EntityDetail


@pytest.mark.django_db
class TestEntityAPI:
    def setup_method(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.token, _ = Token.objects.get_or_create(user=self.user)

        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

        self.uid = uuid.uuid4()

    def test_create_entity(self):
        url = reverse("entity-list")
        data = {
            "entity_uid": str(self.uid),
            "entity_type": "PERSON",
            "display_name": "Alic",
            "details": [
                {"detail_code": "EMAIL", "value": {"value": "alic@gmail.com"}}
            ],
        }
        response = self.client.post(url, data, format="json")
        assert response.status_code == 201
        assert response.data["display_name"] == "Alic"
        assert Entity.objects.count() == 1
        assert EntityDetail.objects.count() == 1

    def test_get_entity_list(self):
        self.client.post(reverse("entity-list"), {
            "entity_uid": str(self.uid),
            "entity_type": "PERSON",
            "display_name": "Bogdan",
        }, format="json")

        url = reverse("entity-list")
        response = self.client.get(url)
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["display_name"] == "Bogdan"

    def test_patch_entity_creates_new_version(self):
        self.client.post(reverse("entity-list"), {
            "entity_uid": str(self.uid),
            "entity_type": "PERSON",
            "display_name": "Denis",
        }, format="json")

        url = reverse("entity-detail", args=[self.uid])
        response = self.client.patch(url, {
            "entity_type": "PERSON",
            "display_name": "Denis Arte",
        }, format="json")
        assert response.status_code == 200
        assert response.data["display_name"] == "Denis Arte"

        assert Entity.objects.filter(entity_uid=self.uid).count() == 2
        current = Entity.objects.filter(entity_uid=self.uid, is_current=True).first()
        assert current.display_name == "Denis Arte"

    def test_entity_history(self):
        self.client.post(reverse("entity-list"), {
            "entity_uid": str(self.uid),
            "entity_type": "PERSON",
            "display_name": "Diana",
        }, format="json")

        url = reverse("entity-history", args=[self.uid])
        response = self.client.get(url)
        assert response.status_code == 200
        assert "entities" in response.data
        assert len(response.data["entities"]) >= 1

    def test_entities_asof(self):
        self.client.post(reverse("entity-list"), {
            "entity_uid": str(self.uid),
            "entity_type": "PERSON",
            "display_name": "Eva",
        }, format="json")

        now = timezone.now()

        url = reverse("entity-asof")
        response = self.client.get(url, {"as_of": now.isoformat()})
        assert response.status_code == 200
        assert len(response.data) >= 1

    def test_diff_endpoint(self):
        self.client.post(reverse("entity-list"), {
            "entity_uid": str(self.uid),
            "entity_type": "PERSON",
            "display_name": "Pol",
        }, format="json")

        url = reverse("entity-diff")
        response = self.client.get(url, {"from": "2025-09-01", "to": "2025-09-30"})
        assert response.status_code == 200
        assert isinstance(response.data, list)