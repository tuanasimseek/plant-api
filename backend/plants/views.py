from rest_framework.permissions import IsAuthenticated
from rest_framework import status 
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny

from .models import Plant, Pot, Reading, Command
from .serializers import PlantSerializer, PotSerializer, ReadingSerializer, CommandSerializer
from .device_auth import DeviceTokenAuthentication

#plant 
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def plant_list(request):
    qs = Plant.objects.all().order_by("id")
    category = request.query_params.get("category")
    if category:
        qs = qs.filter(category=category)

    serializer = PlantSerializer(qs, many=True)
    return Response(serializer.data)

@api_view(["GET"])
@permission_classes((IsAuthenticated))
def plant_detail(request,plant_id:int):
    plant = get_object_or_404(Plant, id=plant_id)
    serializer = PlantSerializer(plant)
    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def plant_categories(request):
    categories = (
        Plant.objects.exclude(category="")
        .values_list("category",flat=True)
        .distinct()
        .order_by("category")
    )
    return Response(list(categories))

#pot
@api_view(["GET","POST"])
@permission_classes([IsAuthenticated])
def pot_list_create(request):
    if request.method == "GET":
        pots = Pot.objects.filter(owner=request.user).order_by("id")#get
        return Response(PotSerializer(pots,many=True).data)
    
    serializer = PotSerializer(data=request.data)#post
    if serializer.is_valid():
        serializer.save(owner=request.user)
        return Response(serializer.data,status=status.HTTP_201_CREATED)
    return Response(serializer.errors,status=status.HTTP_404_BAD_REQUEST)

@api_view(["GET" ,"PATCH"])
@permission_classes([IsAuthenticated])
def pot_detail_patch(request,pot_id:int):
    pot = get_object_or_404(Pot,id=pot_id,owner=request.user)

    if request.method == "GET":
        return Response(PotSerializer(pot).data)
    
    serializer = PotSerializer(pot, data=request.data, partial=True)#patch saksıya bıtkı atama 
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors,status=status.HTTP_404_BAD_REQUEST)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def pot_latest_reading(request,pot_id:int):
    pot = get_object_or_404(Pot,id=pot_id,owner=request.user)
    latest = pot.readings.first()
    if not latest:
        return Response({"detail":"No readings"}, status=status.HTTP_404_NOT_FOUND)
    return Response(ReadingSerializer(latest).data)

#reading esp
@api_view(["POST"])
@authentication_classes([DeviceTokenAuthentication])
@permission_classes([AllowAny])
def reading_create_device(request):
    pot = request.auth
    data = request.data.copy()
    data["pot"] = pot.id
    serializer = ReadingSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#commands 
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def pot_command_create(request,pot_id:int):
    pot = get_object_or_404(Pot, id=pot_id,owner=request.user)
    data = request.data.copy()
    data["pot"] = pot.id

    serializer = CommandSerializer(data=data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET"])
@authentication_classes([DeviceTokenAuthentication])
@permission_classes([AllowAny])
def pot_pending_commands_device(request,pot_id:int):
    pot_from_token = request.auth
    if pot_from_token is None:
        return Response({"detail":""},status=status.HTTP_401_UNAUTHORIZED)
    if pot_from_token.id != pot_id:
        return Response({"detail": ""},status=status.HTTP_403_FORBIDDEN)
    
    cmds = Command.objects.filter(pot_id=pot_id,status=Command.STATUS_PENDING).order_by("created_at")
    return Response(CommandSerializer(cmds,many=True).data, status=status.HTTP_200_OK)

@api_view(["PATCH"])
@authentication_classes([DeviceTokenAuthentication])
@permission_classes([AllowAny])
def command_update_status_device(request, command_id:int):
    pot_from_token = request.auth

    if pot_from_token is None:
        return Response({"detail":"x device token missing"},status=status.HTTP_401_UNAUTHORİZED)

    cmd = get_object_or_404(Command, id=command_id)

    if cmd.pot_id != pot_from_token.id:
        return Response({"detail": "forbidden"},status=status.HTTP_403_FORBIDDEN)
    
    new_status = request.data.get("status")
    if new_status not in [Command.STATUS_DONE, Command.STATUS_FAILED]:
        return Response({"detail": ""},status=status.HTTP_400_REQUEST)
    
    cmd.status = new_status
    cmd.save(update_fields=["status"])
    return Response(CommandSerializer(cmd).data,status=status.HTTP_200_OK)
