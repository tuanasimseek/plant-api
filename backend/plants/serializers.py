from rest_framework import serializers
from .models import Plant


class PlantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plant
        fields = (
            'id', 'name', 'scientific_name', 'category',
            'description', 'watering_interval_days', 'light_requirement',
            'temperature_min', 'temperature_max', 'image_url'
        )

        