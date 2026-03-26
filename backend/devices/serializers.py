from rest_framework import serializers
from .models import Device


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = (
            'id', 'device_code', 'model', 'firmware_version',
            'status', 'battery_level', 'last_seen_at', 'registered_at'
        )