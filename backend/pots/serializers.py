from rest_framework import serializers
from .models import Pot
from plants.serializers import PlantSerializer
from sensors.models import SensorReading


class PotSerializer(serializers.ModelSerializer):
    plant = PlantSerializer(read_only=True)
    device_id = serializers.CharField(source='device.device_code', read_only=True)
    device_status = serializers.CharField(source='device.status', read_only=True)
    last_update = serializers.DateTimeField(source='updated_at', read_only=True)

    class Meta:
        model = Pot
        fields = (
            'id', 'device_id', 'plant', 'nickname',
            'is_active', 'placement_status', 'device_status', 'last_update'
        )


class PotDetailSerializer(serializers.ModelSerializer):
    
    plant = PlantSerializer(read_only=True)
    device_id = serializers.CharField(source='device.device_code', read_only=True)
    device_status = serializers.CharField(source='device.status', read_only=True)
    last_reading = serializers.SerializerMethodField()
    last_update = serializers.DateTimeField(source='updated_at', read_only=True)

    class Meta:
        model = Pot
        fields = (
            'id', 'device_id', 'plant', 'nickname',
            'is_active', 'placement_status', 'device_status',
            'last_reading', 'last_update'
        )

    def get_last_reading(self, obj):
        reading = SensorReading.objects.filter(pot=obj).order_by('-recorded_at').first()
        if reading:
            return {
                "temperature": reading.temperature,
                "humidity": reading.humidity,
                "soil_moisture": reading.soil_moisture,
                "light": reading.light,
                "water_level": reading.water_level,
            }
        return None
    