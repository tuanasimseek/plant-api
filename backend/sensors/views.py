from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from .models import SensorReading, WateringHistory
from .serializers import SensorReadingSerializer, WateringHistorySerializer
from pots.models import Pot
from devices.models import Device
from ml.models import StateMachineConfig


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


class SendSensorReadingsView(APIView):
    permission_classes = []

    def post(self, request, pot_id):
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

        SensorReading.objects.create(
            pot=pot,
            temperature=request.data.get('temperature'),
            humidity=request.data.get('humidity'),
            soil_moisture=request.data.get('soil_moisture'),
            light=request.data.get('light'),
            water_level=request.data.get('water_level'),
            recorded_at=timezone.now(),
        )

        return Response({
            "status": "success",
            "message": "Sensor readings saved successfully"
        }, status=status.HTTP_201_CREATED)


class GetPotConfigView(APIView):
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

        config = StateMachineConfig.objects.first()
        if not config:
            return Response({
                "status": "error",
                "message": "Config bulunamadı."
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            "status": "success",
            "data": {
                "pot_id": pot.id,
                "moisture_threshold": config.moisture_threshold,
                "watering_duration_ms": config.watering_duration_ms,
                "sleep_interval_min": config.sleep_interval_min,
                "auto_mode": config.auto_mode,
            }
        }, status=status.HTTP_200_OK)


class UpdateDeviceStatusView(APIView):
    permission_classes = []

    def patch(self, request, pot_id):
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

        device.status = request.data.get('device_status', device.status)
        device.is_watering = request.data.get('is_watering', device.is_watering)
        device.last_action = request.data.get('last_action', device.last_action)
        device.battery_level = request.data.get('battery_level', device.battery_level)
        device.last_seen_at = timezone.now()
        device.save()

        return Response({
            "status": "success",
            "message": "Device status updated successfully"
        }, status=status.HTTP_200_OK)


class GetPotStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pot_id):
        try:
            pot = Pot.objects.get(id=pot_id, owner=request.user)
        except Pot.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Saksı bulunamadı."
            }, status=status.HTTP_404_NOT_FOUND)

        last_reading = SensorReading.objects.filter(pot=pot).order_by('-recorded_at').first()

        return Response({
            "status": "success",
            "data": {
                "pot_id": pot.id,
                "device_status": pot.device.status,
                "is_watering": pot.device.is_watering,
                "last_action": pot.device.last_action,
                "temperature": last_reading.temperature if last_reading else None,
                "humidity": last_reading.humidity if last_reading else None,
                "soil_moisture": last_reading.soil_moisture if last_reading else None,
                "light": last_reading.light if last_reading else None,
                "water_level": last_reading.water_level if last_reading else None,
                "last_update": last_reading.recorded_at if last_reading else None,
            }
        }, status=status.HTTP_200_OK)


class GetSensorHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pot_id):
        try:
            pot = Pot.objects.get(id=pot_id, owner=request.user)
        except Pot.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Saksı bulunamadı."
            }, status=status.HTTP_404_NOT_FOUND)

        readings = SensorReading.objects.filter(pot=pot).order_by('-recorded_at')

        range_param = request.query_params.get('range')
        start_date = request.query_params.get('startDate')
        end_date = request.query_params.get('endDate')

        if range_param == 'day':
            from datetime import timedelta
            readings = readings.filter(recorded_at__gte=timezone.now() - timedelta(days=1))
        elif range_param == 'week':
            from datetime import timedelta
            readings = readings.filter(recorded_at__gte=timezone.now() - timedelta(weeks=1))
        elif range_param == 'month':
            from datetime import timedelta
            readings = readings.filter(recorded_at__gte=timezone.now() - timedelta(days=30))

        if start_date:
            readings = readings.filter(recorded_at__gte=parse_datetime(start_date))
        if end_date:
            readings = readings.filter(recorded_at__lte=parse_datetime(end_date))

        serializer = SensorReadingSerializer(readings, many=True)
        return Response({
            "status": "success",
            "data": {
                "pot_id": pot.id,
                "history": serializer.data
            }
        }, status=status.HTTP_200_OK)


class GetWateringHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pot_id):
        try:
            pot = Pot.objects.get(id=pot_id, owner=request.user)
        except Pot.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Saksı bulunamadı."
            }, status=status.HTTP_404_NOT_FOUND)

        history = WateringHistory.objects.filter(pot=pot).order_by('-watered_at')

        start_date = request.query_params.get('startDate')
        end_date = request.query_params.get('endDate')

        if start_date:
            history = history.filter(watered_at__gte=parse_datetime(start_date))
        if end_date:
            history = history.filter(watered_at__lte=parse_datetime(end_date))

        serializer = WateringHistorySerializer(history, many=True)
        return Response({
            "status": "success",
            "data": {
                "pot_id": pot.id,
                "history": serializer.data
            }
        }, status=status.HTTP_200_OK)