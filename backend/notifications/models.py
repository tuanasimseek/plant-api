from django.db import models
from django.conf import settings
from pots.models import Pot


class Notification(models.Model):
    TYPE_CHOICES = (
        ('watering', 'Watering'),
        ('analysis', 'Analysis'),
        ('alert', 'Alert'),
        ('system', 'System'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    pot = models.ForeignKey(Pot, on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='system')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.user.username}"


class Alert(models.Model):
    SEVERITY_CHOICES = (
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
    )

    pot = models.ForeignKey(Pot, on_delete=models.CASCADE, related_name='alerts')
    type = models.CharField(max_length=50)
    message = models.TextField()
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='warning')
    resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type} - {self.severity} - Pot {self.pot_id}"