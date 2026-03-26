from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser

from .models import PlantImage, AnalysisResult
from .serializers import PlantImageSerializer, AnalysisResultSerializer
from plants.models import Plant
from pots.models import Pot


class UploadPlantImageView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, plant_id):
        try:
            plant = Plant.objects.get(id=plant_id)
        except Plant.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Bitki bulunamadı."
            }, status=status.HTTP_404_NOT_FOUND)

        image_file = request.FILES.get('image')
        if not image_file:
            return Response({
                "status": "error",
                "message": "Görüntü zorunludur."
            }, status=status.HTTP_400_BAD_REQUEST)

        plant_image = PlantImage.objects.create(
            plant=plant,
            image=image_file,
            source=request.data.get('source'),
            captured_at=request.data.get('captured_at'),
        )

        return Response({
            "status": "success",
            "data": {
                "image_id": plant_image.id,
                "plant_id": plant.id,
                "image_url": plant_image.image.url,
                "uploaded_at": plant_image.uploaded_at,
            }
        }, status=status.HTTP_201_CREATED)


class AnalyzePlantImageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        plant_id = request.data.get('plant_id')
        image_url = request.data.get('image_url')

        if not plant_id or not image_url:
            return Response({
                "status": "error",
                "message": "plant_id ve image_url zorunludur."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            plant = Plant.objects.get(id=plant_id)
        except Plant.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Bitki bulunamadı."
            }, status=status.HTTP_404_NOT_FOUND)

        # ML modeli hazır olunca buraya entegre edilecek
        # Şimdilik mock response
        result = AnalysisResult.objects.create(
            plant=plant,
            health_status='healthy',
            disease_detected=False,
            confidence=0.91,
            species_prediction=plant.scientific_name,
        )

        return Response({
            "status": "success",
            "data": AnalysisResultSerializer(result).data
        }, status=status.HTTP_200_OK)


class MeasurePlantHeightView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        plant_id = request.data.get('plant_id')
        image_url = request.data.get('image_url')
        reference_object_cm = request.data.get('reference_object_cm', 10)

        if not plant_id or not image_url:
            return Response({
                "status": "error",
                "message": "plant_id ve image_url zorunludur."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            plant = Plant.objects.get(id=plant_id)
        except Plant.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Bitki bulunamadı."
            }, status=status.HTTP_404_NOT_FOUND)

        # ML modeli hazır olunca buraya entegre edilecek
        return Response({
            "status": "success",
            "data": {
                "plant_id": plant.id,
                "estimated_height_cm": 24.7,
                "confidence": 0.87,
                "model_version": "height_estimator_v1"
            }
        }, status=status.HTTP_200_OK)


class MeasurePlantHeightLiveView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        image_file = request.FILES.get('image')
        if not image_file:
            return Response({
                "status": "error",
                "message": "Görüntü zorunludur."
            }, status=status.HTTP_400_BAD_REQUEST)

        # ML modeli hazır olunca buraya entegre edilecek
        return Response({
            "status": "success",
            "data": {
                "estimated_height_cm": 24.7,
                "confidence": 0.87,
                "model_version": "height_estimator_v1"
            }
        }, status=status.HTTP_200_OK)


class AnalyzeGrowthView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        plant_id = request.data.get('plant_id')
        current_image_url = request.data.get('current_image_url')
        previous_image_url = request.data.get('previous_image_url')

        if not plant_id or not current_image_url or not previous_image_url:
            return Response({
                "status": "error",
                "message": "plant_id, current_image_url ve previous_image_url zorunludur."
            }, status=status.HTTP_400_BAD_REQUEST)

        # ML modeli hazır olunca buraya entegre edilecek
        return Response({
            "status": "success",
            "data": {
                "plant_id": plant_id,
                "growth_status": "growing",
                "growth_rate": 1.8,
                "height_difference_cm": 2.3
            }
        }, status=status.HTTP_200_OK)


class ClassifyPlantSpeciesView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        plant_id = request.data.get('plant_id')
        image_url = request.data.get('image_url')

        if not plant_id or not image_url:
            return Response({
                "status": "error",
                "message": "plant_id ve image_url zorunludur."
            }, status=status.HTTP_400_BAD_REQUEST)

        # ML modeli hazır olunca buraya entegre edilecek
        return Response({
            "status": "success",
            "data": {
                "plant_id": plant_id,
                "plant_species": "Monstera Deliciosa",
                "confidence": 0.94,
                "model_version": "plant_classifier_v1"
            }
        }, status=status.HTTP_200_OK)


class GetAIAnalysisResultView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pot_id):
        try:
            pot = Pot.objects.get(id=pot_id, owner=request.user)
        except Pot.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Saksı bulunamadı."
            }, status=status.HTTP_404_NOT_FOUND)

        result = AnalysisResult.objects.filter(pot=pot).order_by('-analyzed_at').first()
        if not result:
            return Response({
                "status": "error",
                "message": "Analiz sonucu bulunamadı."
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            "status": "success",
            "data": {
                "pot_id": pot.id,
                "plant_health": result.health_status,
                "suggestion": result.suggestion,
                "height_cm": result.estimated_height_cm,
                "growth_status": result.growth_status,
                "analyzed_at": result.analyzed_at,
            }
        }, status=status.HTTP_200_OK)


class GetPlantHealthHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, plant_id):
        try:
            plant = Plant.objects.get(id=plant_id)
        except Plant.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Bitki bulunamadı."
            }, status=status.HTTP_404_NOT_FOUND)

        history = AnalysisResult.objects.filter(
            plant=plant
        ).order_by('-analyzed_at').values(
            'analyzed_at', 'health_status', 'disease_name', 'estimated_height_cm'
        )

        return Response({
            "status": "success",
            "data": {
                "plant_id": plant.id,
                "history": list(history)
            }
        }, status=status.HTTP_200_OK)


class GuestAIScanView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        image_file = request.FILES.get('image')
        if not image_file:
            return Response({
                "status": "error",
                "message": "Görüntü zorunludur."
            }, status=status.HTTP_400_BAD_REQUEST)

        # ML modeli hazır olunca buraya entegre edilecek
        return Response({
            "status": "success",
            "data": {
                "plant": "Rose",
                "health": "Healthy",
                "confidence": 0.91
            }
        }, status=status.HTTP_200_OK)


class MemberAIChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        plant_id = request.data.get('plant_id')
        question = request.data.get('question')

        if not question:
            return Response({
                "status": "error",
                "message": "Soru zorunludur."
            }, status=status.HTTP_400_BAD_REQUEST)

        # AI chat modeli hazır olunca buraya entegre edilecek
        return Response({
            "status": "success",
            "data": {
                "answer": "Yaprakların sararması genellikle fazla sulama veya düşük ışık seviyesinden kaynaklanabilir. Toprak nem seviyesini kontrol etmeniz önerilir."
            }
        }, status=status.HTTP_200_OK)