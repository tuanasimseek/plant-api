from django.db import models
from django.conf import settings
from plants.models import Plant
from devices.models import Device


class Pot(models.Model):
    PLACEMENT_CHOICES = (
        ('suitable', 'Suitable'),
        ('unsuitable', 'Unsuitable'),
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='pots'
    )
    allowed_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='shared_pots',
        blank=True
    )

    plant = models.ForeignKey(
        Plant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pots'
    )
    device = models.OneToOneField(
        Device,
        on_delete=models.CASCADE,
        related_name='pot'
    )

    nickname = models.CharField(max_length=150, blank=True, null=True)
    is_active = models.BooleanField(default=False)
    placement_status = models.CharField(max_length=20, choices=PLACEMENT_CHOICES, blank=True, null=True)

    moisture_threshold = models.FloatField(default=30.0)
    watering_duration_ms = models.IntegerField(default=5000)
    sleep_interval_min = models.IntegerField(default=15)
    auto_mode = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nickname or f"Pot {self.id}"
    
class FuzzyLog(models.Model):
    pot = models.ForeignKey(
        Pot,
        on_delete=models.CASCADE,
        related_name='fuzzy_logs'
    )
    recorded_at = models.DateTimeField()
    memberships = models.JSONField()
    firing_rules = models.JSONField()
    centroid = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-recorded_at']

    def __str__(self):
        return f"FuzzyLog Pot {self.pot.id} - {self.recorded_at}"