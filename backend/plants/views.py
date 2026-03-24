from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Plant
from .serializers import PlantSerializer


class PlantListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        plants = Plant.objects.all()
        serializer = PlantSerializer(plants, many=True)
        return Response({
            "status": "success",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class PlantCategoryListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        categories = Plant.objects.exclude(
            category=None
        ).exclude(
            category=''
        ).values_list('category', flat=True).distinct()
        
        data = [{"id": i+1, "name": cat} for i, cat in enumerate(categories)]
        return Response({
            "status": "success",
            "data": data
        }, status=status.HTTP_200_OK)


class PlantSearchView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        q = request.query_params.get('q', None)
        if not q:
            return Response({
                "status": "error",
                "message": "q parametresi zorunludur."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        plants = Plant.objects.filter(name__icontains=q) | Plant.objects.filter(scientific_name__icontains=q)
        serializer = PlantSerializer(plants, many=True)
        return Response({
            "status": "success",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class PlantDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, plant_id):
        try:
            plant = Plant.objects.get(id=plant_id)
        except Plant.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Bitki bulunamadı."
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = PlantSerializer(plant)
        return Response({
            "status": "success",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    