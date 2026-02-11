from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .data import PLANTS
from .serializers import PlantSerializer

@api_view(["GET"])
def plant_list(request):
    serializer = PlantSerializer(PLANTS, many=True)
    return Response(serializer.data)