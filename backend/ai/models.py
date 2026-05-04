from django.db import models
from pots.models import Pot
from plants.models import Plant


class PlantImage(models.Model):
    SOURCE_CHOICES = (
        ('mobile', 'Mobile'),
        ('device', 'Device'),
        ('web', 'Web'),
    )

    pot = models.ForeignKey(Pot, on_delete=models.CASCADE, related_name='plant_images', blank=True, null=True)
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, related_name='images', blank=True, null=True)
    image = models.ImageField(upload_to='plants/')
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, blank=True, null=True)
    captured_at = models.DateTimeField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image {self.id} - Plant {self.plant_id}"


class AnalysisResult(models.Model):
    HEALTH_CHOICES = (
        ('healthy', 'Healthy'),
        ('slightly_stressed', 'Slightly Stressed'),
        ('unhealthy', 'Unhealthy'),
    )
    GROWTH_CHOICES = (
        ('growing', 'Growing'),
        ('stable', 'Stable'),
        ('declining', 'Declining'),
    )

    pot = models.ForeignKey(Pot, on_delete=models.CASCADE, related_name='analysis_results', blank=True, null=True)
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, related_name='analysis_results', blank=True, null=True)
    image = models.ForeignKey(PlantImage, on_delete=models.SET_NULL, null=True, blank=True)
    health_status = models.CharField(max_length=30, choices=HEALTH_CHOICES, blank=True, null=True)
    disease_detected = models.BooleanField(default=False)
    disease_name = models.CharField(max_length=100, blank=True, null=True)
    wilting_level = models.FloatField(blank=True, null=True)
    dryness_level = models.FloatField(blank=True, null=True)
    estimated_height_cm = models.FloatField(blank=True, null=True)
    growth_status = models.CharField(max_length=20, choices=GROWTH_CHOICES, blank=True, null=True)
    growth_rate = models.FloatField(blank=True, null=True)
    species_prediction = models.CharField(max_length=150, blank=True, null=True)
    confidence = models.FloatField(blank=True, null=True)
    suggestion = models.TextField(blank=True, null=True)
    analyzed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Analysis {self.id} - {self.health_status}"
    
class OptimalDecision(models.Model):
    pot = models.ForeignKey('pots.Pot', on_delete=models.CASCADE)
    watering_needed = models.BooleanField()
    recommended_watering_ml = models.FloatField()
    light_adjustment = models.CharField(max_length=20)
    temperature_adjustment = models.CharField(max_length=20)
    confidence = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)