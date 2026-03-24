from django.db import models
from pots.models import Pot


class SensorReading(models.Model):
    pot = models.ForeignKey(Pot, on_delete=models.CASCADE, related_name='sensor_readings')
    temperature = models.FloatField(blank=True, null=True)
    humidity = models.FloatField(blank=True, null=True)
    soil_moisture = models.FloatField(blank=True, null=True)
    light = models.FloatField(blank=True, null=True)
    water_level = models.FloatField(blank=True, null=True)
    recorded_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pot {self.pot.id} - {self.recorded_at}"


class WateringHistory(models.Model):
    TRIGGER_CHOICES = (
        ('automatic', 'Automatic'),
        ('manual', 'Manual'),
    )

    pot = models.ForeignKey(Pot, on_delete=models.CASCADE, related_name='watering_history')
    duration_sec = models.IntegerField(blank=True, null=True)
    water_amount_ml = models.FloatField(blank=True, null=True)
    trigger_type = models.CharField(max_length=20, choices=TRIGGER_CHOICES, default='automatic')
    watered_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pot {self.pot.id} - {self.trigger_type} - {self.watered_at}"