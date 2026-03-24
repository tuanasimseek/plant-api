from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
import secrets

from .models import Pot
from .serializers import PotSerializer, PotDetailSerializer
from devices.models import Device
from plants.models import Plant


class VerifyPotQRView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, device_id):
        
        try:
            device = Device.objects.get(device_code=device_id)
        except Device.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Cihaz bulunamadı."
            }, status=status.HTTP_404_NOT_FOUND)

        if hasattr(device, 'pot') and device.pot.is_active:
            if device.pot.owner != request.user:
                return Response({
                    "status": "error",
                    "message": "Bu cihaz başka bir kullanıcıya bağlı."
                }, status=status.HTTP_409_CONFLICT)

        return Response({
            "status": "success",
            "data": {
                "device_id": device.device_code,
                "model": device.model,
                "activated": hasattr(device, 'pot') and device.pot.is_active
            }
        }, status=status.HTTP_200_OK)


class RegisterPotDeviceView(APIView):
    permission_classes = []

    def post(self, request):
        device_id = request.data.get('device_id')
        model = request.data.get('model')
        firmware_version = request.data.get('firmware_version')

        if not device_id:
            return Response({
                "status": "error",
                "message": "device_id zorunludur."
            }, status=status.HTTP_400_BAD_REQUEST)

        if Device.objects.filter(device_code=device_id).exists():
            return Response({
                "status": "error",
                "message": "Bu cihaz zaten kayıtlı."
            }, status=status.HTTP_409_CONFLICT)

        device_token = secrets.token_hex(32)
        device = Device.objects.create(
            device_code=device_id,
            model=model,
            firmware_version=firmware_version,
            device_token=device_token,
        )

        return Response({
            "status": "success",
            "message": "Device registered successfully",
            "device": {
                "device_id": device.device_code,
                "model": device.model,
                "registered": True,
                "device_token": device_token
            }
        }, status=status.HTTP_201_CREATED)


class ActivatePotView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        device_id = request.data.get('device_id')

        if not device_id:
            return Response({
                "status": "error",
                "message": "device_id zorunludur."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            device = Device.objects.get(device_code=device_id)
        except Device.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Cihaz bulunamadı."
            }, status=status.HTTP_404_NOT_FOUND)

        if hasattr(device, 'pot'):
            return Response({
                "status": "error",
                "message": "Bu cihaz zaten aktif veya başka kullanıcıya bağlı."
            }, status=status.HTTP_409_CONFLICT)

        pot = Pot.objects.create(
            owner=request.user,
            device=device,
            is_active=True,
        )

        return Response({
            "status": "success",
            "message": "Pot activated successfully",
            "data": {
                "pot_id": pot.id,
                "device_id": device.device_code,
                "activated": True
            }
        }, status=status.HTTP_200_OK)


class AssignPlantToPotView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pot_id):
        plant_id = request.data.get('plant_id')

        if not plant_id:
            return Response({
                "status": "error",
                "message": "plant_id zorunludur."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            pot = Pot.objects.get(id=pot_id, owner=request.user)
        except Pot.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Saksı bulunamadı."
            }, status=status.HTTP_404_NOT_FOUND)


        try:
            plant = Plant.objects.get(id=plant_id)
        except Plant.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Bitki bulunamadı."
            }, status=status.HTTP_404_NOT_FOUND)

        pot.plant = plant
        pot.save()

        return Response({
            "status": "success",
            "message": "Plant assigned to pot successfully",
            "data": {
                "pot_id": pot.id,
                "plant_id": plant.id,
                "plant_name": plant.name
            }
        }, status=status.HTTP_200_OK)


class PotListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        pots = Pot.objects.filter(owner=request.user).select_related('plant', 'device')
        serializer = PotSerializer(pots, many=True)
        return Response({
            "status": "success",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class PotDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pot_id):
        try:
            pot = Pot.objects.get(id=pot_id, owner=request.user)
        except Pot.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Saksı bulunamadı."
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = PotDetailSerializer(pot)
        return Response({
            "status": "success",
            "data": serializer.data
        }, status=status.HTTP_200_OK)