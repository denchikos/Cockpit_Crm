from django.urls import path
from .views import EntityListCreateView, EntityRetrieveUpdateView, EntityHistoryView, EntityAsOfView, DiffView

urlpatterns = [
    path('entities', EntityListCreateView.as_view(), name='entity-list'),
    path('entities/<uuid:entity_uid>', EntityRetrieveUpdateView.as_view(), name='entity-detail'),
    path('entities/<uuid:entity_uid>/history', EntityHistoryView.as_view(), name='entity-history'),
    path('entities-asof', EntityAsOfView.as_view(), name='entity-asof'),
    path('diff', DiffView.as_view(), name='entity-diff'),
]

