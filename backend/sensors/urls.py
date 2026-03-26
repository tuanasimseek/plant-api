from django.urls import path
from .views import (
    SendSensorReadingsView,
    GetPotConfigView,
    UpdateDeviceStatusView,
    GetPotStatusView,
    GetSensorHistoryView,
    GetWateringHistoryView,
)

urlpatterns = [
    path('pots/<int:pot_id>/readings', SendSensorReadingsView.as_view(), name='send-readings'),
    path('pots/<int:pot_id>/config', GetPotConfigView.as_view(), name='pot-config'),
    path('pots/<int:pot_id>/status', UpdateDeviceStatusView.as_view(), name='update-device-status'),
    path('pots/<int:pot_id>/status', GetPotStatusView.as_view(), name='get-pot-status'),
    path('pots/<int:pot_id>/history', GetSensorHistoryView.as_view(), name='sensor-history'),
    path('pots/<int:pot_id>/watering-history', GetWateringHistoryView.as_view(), name='watering-history'),
]