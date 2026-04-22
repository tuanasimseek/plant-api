from rest_framework import serializers
from django.conf import settings
from .models import Plant


class PlantSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Plant
        fields = [
            'id',
            'name',
            'scientific_name',
            'category',
            'description',
            'watering_interval_days',
            'light_requirement',
            'temperature_min',
            'temperature_max',
            'image',
        ]

    def get_image(self, obj):
        if obj.image:
            return f"{settings.PUBLIC_BASE_URL}{obj.image.url}"
        return None