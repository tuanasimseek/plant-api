from django.urls import path
from .views import (
    HeartbeatView,
    LogActionView,
    DeviceErrorView,
    FirmwareCheckView,
    ActuatorCommandView,
    GetSetupCheckView,
    GetEnvironmentView,
    GetNewConfigView,
)

urlpatterns = [
    path('heartbeat', HeartbeatView.as_view(), name='heartbeat'),
    path('logs/action', LogActionView.as_view(), name='log-action'),
    path('logs/error', DeviceErrorView.as_view(), name='device-error'),
    path('firmware/check', FirmwareCheckView.as_view(), name='firmware-check'),
    path('pots/<int:pot_id>/commands', ActuatorCommandView.as_view(), name='actuator-command'),
    path('pots/<int:pot_id>/setup-check', GetSetupCheckView.as_view(), name='setup-check'),
    path('environment', GetEnvironmentView.as_view(), name='environment'),
    path('pots/<int:pot_id>/newconfig', GetNewConfigView.as_view(), name='new-config'),
]
