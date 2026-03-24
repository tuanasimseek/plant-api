from django.db import models
from django.conf import settings
from plants.models import Plant
from devices.models import Device


class Pot(models.Model):
    PLACEMENT_CHOICES = (
        ('suitable', 'Suitable'),
        ('unsuitable', 'Unsuitable'),
    )

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pots')
    plant = models.ForeignKey(Plant, on_delete=models.SET_NULL, null=True, blank=True, related_name='pots')
    device = models.OneToOneField(Device, on_delete=models.CASCADE, related_name='pot')

    nickname = models.CharField(max_length=150, blank=True, null=True)
    is_active = models.BooleanField(default=False)
    placement_status = models.CharField(max_length=20, choices=PLACEMENT_CHOICES, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nickname or f"Pot {self.id}"
    