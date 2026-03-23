from django.db import models
from django.conf import settings
from plants.models import Plant
from devices.models import Device


class Pot(models.Model):

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE)
    device = models.OneToOneField(Device, on_delete=models.CASCADE)

    name = models.CharField(max_length=150)
    location = models.CharField(max_length=150, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name