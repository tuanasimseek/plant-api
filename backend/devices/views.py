from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q

from .models import Device
from .serializers import DeviceSerializer
from pots.models import Pot
from sensors.models import SensorReading, WateringHistory


def get_device_from_token(request):
    device_token = request.headers.get('X-Device-Token')
    if not device_token:
        return None, Response({
            "status": "error",
            "message": "Device token gerekli."
        }, status=status.HTTP_401_UNAUTHORIZED)
    try:
        device = Device.objects.get(device_token=device_token)
        return device, None
    except Device.DoesNotExist:
        return None, Response({
            "status": "error",
            "message": "Geçersiz device token."
        }, status=status.HTTP_403_FORBIDDEN)


class HeartbeatView(APIView):
    permission_classes = []

    def post(self, request):
        device, error = get_device_from_token(request)
        if error:
            return error

        device.status = 'online'
        device.last_seen_at = timezone.now()
        device.save()

        return Response({
            "status": "success",
            "message": "Heartbeat received"
        }, status=status.HTTP_200_OK)


class LogActionView(APIView):
    permission_classes = []

    def post(self, request):
        device, error = get_device_from_token(request)
        if error:
            return error

        action_type = request.data.get('action_type')
        trigger_source = request.data.get('trigger_source', 'auto')

        if action_type == 'watering':
            try:
                pot = Pot.objects.get(device=device)
                WateringHistory.objects.create(
                    pot=pot,
                    duration_sec=request.data.get('duration_sec'),
                    trigger_type=trigger_source,
                    watered_at=timezone.now(),
                )
            except Pot.DoesNotExist:
                pass

        return Response({
            "status": "success",
            "message": "Action log saved successfully"
        }, status=status.HTTP_201_CREATED)


class DeviceErrorView(APIView):
    permission_classes = []

    def post(self, request):
        device, error = get_device_from_token(request)
        if error:
            return error

        try:
            pot = Pot.objects.get(device=device)
            from notifications.models import Alert
            Alert.objects.create(
                pot=pot,
                type=request.data.get('error_code', 'device_error'),
                message=request.data.get('error_message', ''),
                severity=request.data.get('severity', 'critical'),
            )
        except Pot.DoesNotExist:
            pass

        return Response({
            "status": "success",
            "message": "Device error logged"
        }, status=status.HTTP_201_CREATED)


class FirmwareCheckView(APIView):
    permission_classes = []

    def get(self, request):
        device, error = get_device_from_token(request)
        if error:
            return error

        current_version = request.query_params.get('current_version', '1.0.0')
        latest_version = '1.1.0'

        if current_version == latest_version:
            return Response({
                "status": "up_to_date",
                "latest_version": latest_version,
            }, status=status.HTTP_200_OK)

        return Response({
            "status": "update_available",
            "latest_version": latest_version,
            "download_url": f"https://server.com/firmware/v{latest_version}.bin"
        }, status=status.HTTP_200_OK)


class ActuatorCommandView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pot_id):
        try:
            pot = Pot.objects.get(
                Q(id=pot_id) & (Q(owner=request.user) | Q(allowed_users=request.user))
            )
        except Pot.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Saksı bulunamadı."
            }, status=status.HTTP_404_NOT_FOUND)

        command = request.data.get('command')
        if command == 'water_on':
            pot.device.is_watering = True
            pot.device.last_action = 'manual_watering_started'
            pot.device.save()
        elif command == 'water_off':
            pot.device.is_watering = False
            pot.device.last_action = 'manual_watering_stopped'
            pot.device.save()
        else:
            return Response({
                "status": "error",
                "message": f"Geçersiz komut: {command}"
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "status": "success",
            "message": "Actuator command queued successfully",
            "data": {
                "pot_id": pot.id,
                "device_id": pot.device.id,
                "device_code": pot.device.device_code,
                "command": command,
            }
        }, status=status.HTTP_200_OK)


class GetSetupCheckView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pot_id):
        try:
            pot = Pot.objects.get(
                Q(id=pot_id) & (Q(owner=request.user) | Q(allowed_users=request.user))
            )
        except Pot.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Saksı bulunamadı."
            }, status=status.HTTP_404_NOT_FOUND)

        last_reading = SensorReading.objects.filter(pot=pot).order_by('-recorded_at').first()

        light_ok = False
        if last_reading and last_reading.light:
            light_ok = last_reading.light >= 200

        placement_status = 'suitable' if light_ok else 'unsuitable'
        pot.placement_status = placement_status
        pot.save()

        return Response({
            "status": "success",
            "data": {
                "pot_id": pot.id,
                "device_code": pot.device.device_code, 
                "light_ok": light_ok,
                "placement_status": placement_status,
                "message": "Konum uygun" if light_ok else "Konum uygun değil"
            }
        }, status=status.HTTP_200_OK)


class GetEnvironmentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        pot_id = request.query_params.get('potId')

        if pot_id:
            try:
                pot = Pot.objects.get(
                    Q(id=pot_id) & (Q(owner=request.user) | Q(allowed_users=request.user))
                )
                last_reading = SensorReading.objects.filter(pot=pot).order_by('-recorded_at').first()
                if last_reading:
                    return Response({
                        "status": "success",
                        "data": {
                            "pot_id": pot.id,
                            "device_code": pot.device.device_code,  
                            "temperature": last_reading.temperature,
                            "humidity": last_reading.humidity,
                            "light_level": last_reading.light,
                            "environment_type": "indoor",
                            "time_of_day": "day"
                        }
                    }, status=status.HTTP_200_OK)
            except Pot.DoesNotExist:
                pass

        return Response({
            "status": "success",
            "data": {
                "temperature": 24.5,
                "humidity": 55,
                "light_level": 420,
                "environment_type": "indoor",
                "time_of_day": "day"
            }
        }, status=status.HTTP_200_OK)


class GetNewConfigView(APIView):
    permission_classes = []

    def get(self, request, pot_id):
        device, error = get_device_from_token(request)
        if error:
            return error

        try:
            pot = Pot.objects.get(id=pot_id, device=device)
        except Pot.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Saksı bulunamadı."
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            "status": "success",
            "data": {
                "pot_id": pot.id,
                "device_db_id": device.id,        # eklendi
                "device_code": device.device_code, # eklendi
                "moisture_threshold": pot.moisture_threshold,
                "watering_duration_ms": pot.watering_duration_ms,
                "sleep_interval_min": pot.sleep_interval_min,
                "auto_mode": pot.auto_mode,
            }
        }, status=status.HTTP_200_OK)