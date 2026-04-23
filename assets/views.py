from __future__ import annotations

import json

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework import mixins, status, viewsets
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Asset, AuditLog, Location
from .serializers import AssetSerializer, LocationSerializer, TelemetrySerializer


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return request.user.is_staff


def broadcast_asset_update(event_type: str, asset: Asset):
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return
    data = {
        'type': event_type,
        'asset': {
            'id': str(asset.id),
            'name': asset.name,
            'asset_type': asset.asset_type,
            'status': asset.status,
            'description': asset.description,
            'created_at': asset.created_at.isoformat(),
            'updated_at': asset.updated_at.isoformat(),
        }
    }
    async_to_sync(channel_layer.group_send)(
        'assets',
        {'type': 'asset_update', 'data': data}
    )


class AssetViewSet(viewsets.ModelViewSet):
    serializer_class = AssetSerializer
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Asset.objects.all().order_by('-created_at')

    def get_queryset(self):
        qs = super().get_queryset()
        status_param = self.request.query_params.get('status')
        asset_type_param = self.request.query_params.get('asset_type')
        if status_param:
            qs = qs.filter(status=status_param)
        if asset_type_param:
            qs = qs.filter(asset_type=asset_type_param)
        return qs

    def perform_create(self, serializer):
        asset = serializer.save()
        AuditLog.objects.create(
            asset=asset,
            action='asset_created',
            performed_by=self.request.user,
            details={'data': self.request.data},
        )
        broadcast_asset_update('asset_created', asset)

    def perform_update(self, serializer):
        asset = serializer.save()
        AuditLog.objects.create(
            asset=asset,
            action='asset_updated',
            performed_by=self.request.user,
            details={'data': self.request.data},
        )
        broadcast_asset_update('asset_updated', asset)

    def perform_destroy(self, instance):
        asset_id = str(instance.id)
        instance.delete()
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                'assets',
                {'type': 'asset_update', 'data': {'type': 'asset_deleted', 'asset': {'id': asset_id}}}
            )


class LocationViewSet(mixins.CreateModelMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = LocationSerializer
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Location.objects.select_related('asset').order_by('-timestamp')

    def get_queryset(self):
        qs = super().get_queryset()
        asset_id = self.request.query_params.get('asset_id')
        if asset_id:
            qs = qs.filter(asset_id=asset_id)
        return qs

    def create(self, request, *args, **kwargs):
        asset_id = request.data.get('asset_id') or request.data.get('asset')
        if not asset_id:
            return Response({'asset_id': ['This field is required.']}, status=status.HTTP_400_BAD_REQUEST)
        try:
            asset = Asset.objects.get(id=asset_id)
        except Asset.DoesNotExist:
            return Response({'asset_id': ['Asset with this id does not exist.']}, status=status.HTTP_400_BAD_REQUEST)

        raw_payload = request.data.get('raw_payload')
        raw_payload_bytes = raw_payload.encode('utf-8') if isinstance(raw_payload, str) else None

        location = Location.objects.create(
            asset=asset,
            latitude=request.data.get('latitude'),
            longitude=request.data.get('longitude'),
            raw_payload=raw_payload_bytes,
        )
        return Response(self.get_serializer(location).data, status=status.HTTP_201_CREATED)


class TelemetryView(APIView):
    permission_classes = (IsAdminOrReadOnly,)

    def post(self, request, *args, **kwargs):
        serializer = TelemetrySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        asset = Asset.objects.get(id=serializer.validated_data['asset_id'])
        raw_payload = serializer.validated_data.get('raw_payload')
        raw_payload_bytes = raw_payload.encode('utf-8') if isinstance(raw_payload, str) else None

        location = Location.objects.create(
            asset=asset,
            latitude=serializer.validated_data['latitude'],
            longitude=serializer.validated_data['longitude'],
            raw_payload=raw_payload_bytes,
        )

        AuditLog.objects.create(
            asset=asset,
            action='telemetry_ping',
            performed_by=request.user,
            details={
                'latitude': str(serializer.validated_data['latitude']),
                'longitude': str(serializer.validated_data['longitude']),
            },
        )

        broadcast_asset_update('telemetry_ping', asset)
        return Response(LocationSerializer(location).data, status=status.HTTP_201_CREATED)


class AssetStatsView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        total = Asset.objects.count()
        active = Asset.objects.filter(status=Asset.Status.ACTIVE).count()
        inactive = Asset.objects.filter(status=Asset.Status.INACTIVE).count()
        lost = Asset.objects.filter(status=Asset.Status.LOST).count()

        return Response({
            'total': total,
            'active': active,
            'inactive': inactive,
            'lost': lost,
            'is_admin': request.user.is_staff,
        })
