from rest_framework import serializers
from .models import Notification, Alert


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = (
            'id', 'title', 'message', 'type',
            'is_read', 'created_at'
        )


class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = (
            'id', 'pot_id', 'type', 'message',
            'severity', 'resolved', 'created_at'
        )