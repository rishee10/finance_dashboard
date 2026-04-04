from rest_framework import generics, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from ..models import FinancialRecord
from ..serializers import FinancialRecordSerializer, FinancialRecordCreateSerializer
from ..permissions import IsAdminRole, IsAnalystOrAbove, IsViewerOrAbove
from ..filters import FinancialRecordFilter


class RecordListCreateView(generics.ListCreateAPIView):
    """
    GET  — viewer, analyst, admin  (all active records, filtered/searched)
    POST — admin only
    """
    filter_backends  = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class  = FinancialRecordFilter
    search_fields    = ['description', 'category']
    ordering_fields  = ['date', 'amount', 'created_at']
    ordering         = ['-date']

    def get_queryset(self):
        # Only return non-deleted records
        return FinancialRecord.objects.filter(is_deleted=False).select_related('created_by')

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminRole()]
        return [IsViewerOrAbove()]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return FinancialRecordCreateSerializer
        return FinancialRecordSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class RecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    — viewer, analyst, admin
    PUT    — admin only
    PATCH  — admin only
    DELETE — admin only (soft delete)
    """
    serializer_class = FinancialRecordSerializer

    def get_queryset(self):
        return FinancialRecord.objects.filter(is_deleted=False).select_related('created_by')

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [IsAdminRole()]
        return [IsViewerOrAbove()]

    def perform_destroy(self, instance):
        # Soft delete — mark as deleted, keep in DB
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted'])