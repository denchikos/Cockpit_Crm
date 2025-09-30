from rest_framework import serializers
from .models import Entity, EntityDetail, EntityType


class EntityTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntityType
        fields = ['code', 'name', 'description']


class EntityDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntityDetail
        fields = ['detail_code', 'value', 'valid_from', 'valid_to', 'is_current']


class EntitySerializer(serializers.ModelSerializer):
    details = serializers.SerializerMethodField()
    entity_type = serializers.SlugRelatedField(slug_field='code', queryset=EntityType.objects.all())

    class Meta:
        model = Entity
        fields = ['entity_uid', 'entity_type', 'display_name', 'valid_from', 'valid_to', 'is_current', 'details']

    def get_details(self, obj):
        qs = EntityDetail.objects.filter(entity_uid=obj.entity_uid, is_current=True)
        return EntityDetailSerializer(qs, many=True).data
