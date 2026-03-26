from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .models import Notification, Alert
from .serializers import NotificationSerializer, AlertSerializer


class GetNotificationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(
            user=request.user
        ).order_by('-created_at')

        status_param = request.query_params.get('status')
        if status_param == 'read':
            notifications = notifications.filter(is_read=True)
        elif status_param == 'unread':
            notifications = notifications.filter(is_read=False)

        serializer = NotificationSerializer(notifications, many=True)
        return Response({
            "status": "success",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class GetAlertsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        alerts = Alert.objects.all().order_by('-created_at')

        pot_id = request.query_params.get('potId')
        alert_type = request.query_params.get('type')
        alert_status = request.query_params.get('status')

        if pot_id:
            alerts = alerts.filter(pot_id=pot_id)
        if alert_type:
            alerts = alerts.filter(type=alert_type)
        if alert_status == 'active':
            alerts = alerts.filter(resolved=False)
        elif alert_status == 'resolved':
            alerts = alerts.filter(resolved=True)

        serializer = AlertSerializer(alerts, many=True)
        return Response({
            "status": "success",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class GetDeviceStateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pot_id):
        from pots.models import Pot
        try:
            pot = Pot.objects.get(id=pot_id, owner=request.user)
        except Pot.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Saksı bulunamadı."
            }, status=status.HTTP_404_NOT_FOUND)

        device = pot.device
        is_watering = device.is_watering
        current_state = "WATERING" if is_watering else "MONITORING"

        return Response({
            "status": "success",
            "data": {
                "pot_id": pot.id,
                "current_state": current_state,
                "previous_state": "MONITORING",
                "updated_at": device.updated_at,
            }
        }, status=status.HTTP_200_OK)


class GetAllDevicesStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from devices.models import Device
        devices = Device.objects.all()

        status_param = request.query_params.get('status')
        if status_param:
            devices = devices.filter(status=status_param)

        data = [{
            "device_id": d.device_code,
            "status": d.status,
            "last_seen": d.last_seen_at,
            "battery_level": d.battery_level,
        } for d in devices]

        return Response({
            "status": "success",
            "data": data
        }, status=status.HTTP_200_OK)