from rest_framework import serializers
from .models import SensorReading, WateringHistory


class SensorReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorReading
        fields = (
            'id', 'temperature', 'humidity',
            'soil_moisture', 'light', 'water_level', 'recorded_at'
        )


class WateringHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = WateringHistory
        fields = (
            'id', 'duration_sec', 'water_amount_ml',
            'trigger_type', 'watered_at'
        )