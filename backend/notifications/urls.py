from django.urls import path
from .views import (
    GetNotificationsView,
    GetAlertsView,
    GetDeviceStateView,
    GetAllDevicesStatusView,
)

urlpatterns = [
    path('notifications', GetNotificationsView.as_view(), name='notifications'),
    path('alerts', GetAlertsView.as_view(), name='alerts'),
    path('pots/<int:pot_id>/state', GetDeviceStateView.as_view(), name='device-state'),
    path('devices/status', GetAllDevicesStatusView.as_view(), name='devices-status'),
]