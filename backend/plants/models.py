from django.db import models


class Plant(models.Model):
    name = models.CharField(max_length=150)
    scientific_name = models.CharField(max_length=150, blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    watering_interval_days = models.IntegerField(blank=True, null=True)
    light_requirement = models.CharField(max_length=50, blank=True, null=True)
    temperature_min = models.FloatField(blank=True, null=True)
    temperature_max = models.FloatField(blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name