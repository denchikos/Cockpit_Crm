from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.dateparse import parse_date
from django.db.models import Q
from django.utils.timezone import make_aware
from django.utils.dateparse import parse_datetime
import datetime
from .models import Entity, EntityDetail, AuditLog
from .serializers import EntitySerializer
from .services import scd2_upsert_entity, scd2_upsert_detail


class EntityListCreateView(generics.ListCreateAPIView):
    queryset = Entity.objects.filter(is_current=True)
    serializer_class = EntitySerializer

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.query_params.get('q')
        entity_type = self.request.query_params.get('type')
        detail_code = self.request.query_params.get('detail_code')

        if q:
            qs = qs.filter(display_name__icontains=q)
        if entity_type:
            qs = qs.filter(entity_type__code=entity_type)
        if detail_code:
            qs = qs.filter(entity_uid__in=EntityDetail.objects.filter(detail_code=detail_code, is_current=True).values("entity_uid"))

        return qs

    def create(self, request, *args, **kwargs):
        data = request.data
        entity_uid = data.get('entity_uid')
        entity_type = data.get('entity_type')
        display_name = data.get('display_name')
        details = data.get('details', [])

        entity = scd2_upsert_entity(entity_uid, entity_type, display_name, actor=str(request.user))

        for d in details:
            scd2_upsert_detail(entity.entity_uid, d['detail_code'], d['value'], actor=str(request.user))

        serializer = self.get_serializer(entity)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class EntityRetrieveUpdateView(APIView):
    def get(self, entity_uid):
        entity = Entity.objects.filter(entity_uid=entity_uid, is_current=True).first()
        if not entity:
            return Response({'detail': 'Not found'}, status=404)
        return Response(EntitySerializer(entity).data)

    def patch(self, request, entity_uid):
        data = request.data
        entity_type = data.get('entity_type')
        display_name = data.get('display_name')
        details = data.get('details', [])

        entity = scd2_upsert_entity(entity_uid, entity_type, display_name, actor=str(request.user))
        for d in details:
            scd2_upsert_detail(entity.entity_uid, d['detail_code'], d['value'], actor=str(request.user))

        return Response(EntitySerializer(entity).data)


class EntityHistoryView(APIView):
    def get(self, request, entity_uid):
        entities = Entity.objects.filter(entity_uid=entity_uid).order_by('valid_from')
        details = EntityDetail.objects.filter(entity_uid=entity_uid).order_by('valid_from')

        return Response({
            'entities': EntitySerializer(entities, many=True).data,
            'details': [{'detail_code': d.detail_code, 'value': d.value, 'valid_from': d.valid_from,
                         'valid_to': d.valid_to} for d in details]
        })


class EntityAsOfView(APIView):
    def get(self, request):
        as_of_str = request.query_params.get('as_of')
        if not as_of_str:
            return Response({'error': 'as_of parameter required'}, status=400)

        as_of = parse_datetime(as_of_str)
        if as_of is None:
            as_of_date = parse_date(as_of_str)
            if not as_of_date:
                return Response({'error': 'Invalid date format'}, status=400)
            as_of = make_aware(datetime.datetime.combine(as_of_date, datetime.time.max))

        qs = Entity.objects.filter(valid_from__lte=as_of).filter(Q(valid_to__isnull=True) | Q(valid_to__gte=as_of))
        return Response(EntitySerializer(qs, many=True).data)


class DiffView(APIView):
    def get(self, request):
        from_date = parse_date(request.query_params.get('from'))
        to_date = parse_date(request.query_params.get('to'))
        if not from_date or not to_date:
            return Response({'error': 'from and to parameters required'}, status=400)
        logs = AuditLog.objects.filter(timestamp__gte=make_aware(datetime.datetime.combine(from_date, datetime.time.min)),
                                       timestamp__lte=make_aware(datetime.datetime.combine(to_date, datetime.time.max)),
                                       )
        result = []
        for log in logs:
            result.append({
                'entity_uid': log.entity_uid,
                'detail_code': log.detail_code,
                'action': log.action,
                'before': log.before,
                'after': log.after,
                'timestamp': log.timestamp,
            })
        return Response(result)