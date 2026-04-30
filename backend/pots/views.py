from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
import secrets

from .models import Pot
from .serializers import PotSerializer, PotDetailSerializer, MyPotSerializer
from devices.models import Device
from plants.models import Plant


class VerifyPotQRView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, device_code):
        try:
            device = Device.objects.get(device_code=device_code)
        except Device.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Cihaz bulunamadı."
            }, status=status.HTTP_404_NOT_FOUND)

        pot = getattr(device, 'pot', None)

        if pot and pot.is_active:
            if pot.owner != request.user and request.user not in pot.allowed_users.all():
                return Response({
                    "status": "error",
                    "message": "Bu cihaz başka bir kullanıcıya bağlı."
                }, status=status.HTTP_409_CONFLICT)

        return Response({
            "status": "success",
            "data": {
                "pot_id": pot.id if pot else None,
                "device_db_id": device.id,           # DB'deki integer id
                "device_code": device.device_code,   # "pot_harun" gibi string
                "model": device.model,
                "activated": pot.is_active if pot else False
            }
        }, status=status.HTTP_200_OK)


class RegisterPotDeviceView(APIView):
    permission_classes = []

    def post(self, request):
        device_code = request.data.get('device_id') 
        model = request.data.get('model')
        firmware_version = request.data.get('firmware_version')

        if not device_code:
            return Response({
                "status": "error",
                "message": "device_id zorunludur."
            }, status=status.HTTP_400_BAD_REQUEST)

        existing_device = Device.objects.filter(device_code=device_code).first()
        if existing_device:
            pot = getattr(existing_device, 'pot', None)
            return Response({
                "status": "success",
                "message": "Device already registered",
                "device": {
                    "device_id": existing_device.id,           
                    "device_code": existing_device.device_code, 
                    "model": existing_device.model,
                    "registered": True,
                    "device_token": existing_device.device_token,
                    "pot_id": pot.id if pot else None,
                    "is_active": pot.is_active if pot else False
                }
            }, status=status.HTTP_200_OK)

        device_token = secrets.token_hex(32)
        device = Device.objects.create(
            device_code=device_code,
            model=model,
            firmware_version=firmware_version,
            device_token=device_token,
        )

        return Response({
            "status": "success",
            "message": "Device registered successfully",
            "device": {
                "device_db_id": device.id,
                "device_code": device.device_code,
                "model": device.model,
                "registered": True,
                "device_token": device_token,
                "pot_id": None,
                "is_active": False
            }
        }, status=status.HTTP_201_CREATED)


class ActivatePotView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        device_code = request.data.get('device_id')  

        if not device_code:
            return Response({
                "status": "error",
                "message": "device_id zorunludur."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            device = Device.objects.get(device_code=device_code)
        except Device.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Cihaz bulunamadı."
            }, status=status.HTTP_404_NOT_FOUND)

        if hasattr(device, 'pot'):
            pot = device.pot
            if pot.owner == request.user or request.user in pot.allowed_users.all():
                return Response({
                    "status": "success",
                    "message": "Bu cihaz zaten sizin hesabınıza bağlı.",
                    "data": {
                        "pot_id": pot.id,
                        "device_id": device.id,          
                        "device_code": device.device_code, 
                        "activated": pot.is_active,
                        "owner": "self",
                        "has_plant": pot.plant is not None
                    }
                }, status=status.HTTP_200_OK)

            return Response({
                "status": "error",
                "message": "Bu cihaz başka bir kullanıcıya bağlı.",
                "data": {
                    "owner": "other",
                    "already_activated": True
                }
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
                "device_db_id": device.id,
                "device_code": device.device_code,
                "activated": True
            }
        }, status=status.HTTP_201_CREATED)


class AssignPlantToPotView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pot_id):
        pot = Pot.objects.filter(
            Q(id=pot_id) & (Q(owner=request.user) | Q(allowed_users=request.user))
        ).distinct().first()

        if not pot:
            return Response({
                "status": "error",
                "message": "Saksı bulunamadı."
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = PotDetailSerializer(pot)
        return Response({
            "status": "success",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request, pot_id):
        plant_id = request.data.get('plant_id')

        if not plant_id:
            return Response({
                "status": "error",
                "message": "plant_id zorunludur."
            }, status=status.HTTP_400_BAD_REQUEST)

        pot = Pot.objects.filter(
            Q(id=pot_id) & (Q(owner=request.user) | Q(allowed_users=request.user))
        ).distinct().first()

        if not pot:
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
                "device_code": pot.device.device_code,  
                "plant_id": plant.id,
                "plant_name": plant.name
            }
        }, status=status.HTTP_200_OK)


class PotListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        pots = Pot.objects.filter(
            Q(owner=request.user) | Q(allowed_users=request.user)
        ).distinct().select_related('plant', 'device')
        serializer = PotSerializer(pots, many=True)
        return Response({
            "status": "success",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class PotDetailView(APIView):
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

        serializer = PotDetailSerializer(pot)
        return Response({
            "status": "success",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class MyPotsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        pots = Pot.objects.filter(owner=request.user).select_related('plant', 'device')
        serializer = MyPotSerializer(pots, many=True)
        return Response({
            "status": "success",
            "data": serializer.data
        }, status=status.HTTP_200_OK)