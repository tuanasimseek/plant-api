from rest_framework import serializers
from .models import PlantImage, AnalysisResult


class PlantImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlantImage
        fields = ('id', 'plant', 'pot', 'image', 'source', 'captured_at', 'uploaded_at')


class AnalysisResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalysisResult
        fields = (
            'id', 'pot', 'plant', 'health_status', 'disease_detected',
            'disease_name', 'wilting_level', 'dryness_level',
            'estimated_height_cm', 'growth_status', 'growth_rate',
            'species_prediction', 'confidence', 'suggestion', 'analyzed_at'
        )