from __future__ import annotations

from rest_framework import serializers

from .models import Asset, AuditLog, Location


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'
        read_only_fields = ('asset',)


class AssetSerializer(serializers.ModelSerializer):
    latest_location = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Asset
        fields = '__all__'

    def get_latest_location(self, obj: Asset):
        latest = obj.locations.order_by('-timestamp').only(
            'latitude',
            'longitude',
            'timestamp',
        ).first()
        if not latest:
            return None
        return {
            'latitude': latest.latitude,
            'longitude': latest.longitude,
            'timestamp': latest.timestamp,
        }


class AuditLogSerializer(serializers.ModelSerializer):
    performed_by = serializers.SlugRelatedField(read_only=True, slug_field='username')

    class Meta:
        model = AuditLog
        fields = '__all__'


class TelemetrySerializer(serializers.Serializer):
    asset_id = serializers.UUIDField()
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    raw_payload = serializers.CharField(required=False, allow_blank=True)

    def validate_asset_id(self, value):
        if not Asset.objects.filter(id=value).exists():
            raise serializers.ValidationError('Asset with this id does not exist.')
        return value
