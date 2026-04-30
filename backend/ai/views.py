import os
import tempfile
from django.db.models import Q


from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser

from .models import PlantImage, AnalysisResult
from .serializers import PlantImageSerializer, AnalysisResultSerializer
from plants.models import Plant
from pots.models import Pot
from .ml_service import predict_plant_height, predict_plant_species, predict_plant_health



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
        reference_object_cm = request.data.get('reference_object_cm', 9)

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

        temp_image_path = None

        try:
            import requests

            response = requests.get(image_url, stream=True, timeout=15)
            response.raise_for_status()

            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        tmp.write(chunk)
                temp_image_path = tmp.name

            # 1) Tür tespiti
            species_result = predict_plant_species(image_path=temp_image_path)

            # 2) Sağlık tespiti
            health_result = predict_plant_health(image_path=temp_image_path)

            # 3) Boy tespiti
            height_result = predict_plant_height(
                image_path=temp_image_path,
                reference_object_cm=float(reference_object_cm)
            )

            # DB'ye tek analiz sonucu olarak kaydet
            result = AnalysisResult.objects.create(
                plant=plant,
                species_prediction=species_result["predicted_species"],
                health_status=health_result["health_status"],
                disease_detected=health_result["disease_detected"],
                disease_name=health_result["disease_name"],
                estimated_height_cm=height_result["estimated_height_cm"],
                confidence=health_result["confidence"],
            )

            return Response({
                "status": "success",
                "data": {
                    "analysis_id": result.id,
                    "plant_id": plant.id,

                    "species_prediction": species_result["predicted_species"],
                    "species_confidence": species_result["confidence"],
                    "species_top_predictions": species_result["top_predictions"],

                    "health_status": health_result["health_status"],
                    "disease_detected": health_result["disease_detected"],
                    "disease_name": health_result["disease_name"],
                    "health_confidence": health_result["confidence"],
                    "health_top_predictions": health_result["top_predictions"],

                    "estimated_height_cm": height_result["estimated_height_cm"],
                    "height_confidence": height_result["confidence"],

                    "models": {
                        "species_model": species_result["model_version"],
                        "health_model": health_result["model_version"],
                        "height_model": height_result["model_version"]
                    }
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": "error",
                "message": f"Analiz başarısız: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        finally:
            if temp_image_path and os.path.exists(temp_image_path):
                os.remove(temp_image_path)


class MeasurePlantHeightView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        plant_id = request.data.get('plant_id')
        image_url = request.data.get('image_url')
        reference_object_cm = request.data.get('reference_object_cm', 9)

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

        try:
            import requests

            response = requests.get(image_url, stream=True, timeout=15)
            response.raise_for_status()

            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        tmp.write(chunk)
                temp_image_path = tmp.name

            result = predict_plant_height(
                image_path=temp_image_path,
                reference_object_cm=float(reference_object_cm)
            )

            # İstersen sonucu DB'ye de kaydedebiliriz
            analysis = AnalysisResult.objects.create(
                plant=plant,
                estimated_height_cm=result["estimated_height_cm"],
                confidence=result["confidence"],
                health_status="unknown"
            )

            return Response({
                "status": "success",
                "data": {
                    "plant_id": plant.id,
                    "estimated_height_cm": result["estimated_height_cm"],
                    "confidence": result["confidence"],
                    "model_version": result["model_version"],
                    "analysis_id": analysis.id,
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": "error",
                "message": f"Boy ölçümü başarısız: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        finally:
            if 'temp_image_path' in locals() and temp_image_path and os.path.exists(temp_image_path):
                os.remove(temp_image_path)

class MeasurePlantHeightLiveView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        image_file = request.FILES.get('image')
        reference_object_cm = request.data.get('reference_object_cm', 9)

        if not image_file:
            return Response({
                "status": "error",
                "message": "Görüntü zorunludur."
            }, status=status.HTTP_400_BAD_REQUEST)

        temp_image_path = None

        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                for chunk in image_file.chunks():
                    tmp.write(chunk)
                temp_image_path = tmp.name

            result = predict_plant_height(
                image_path=temp_image_path,
                reference_object_cm=float(reference_object_cm)
            )

            return Response({
                "status": "success",
                "data": result
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": "error",
                "message": f"Boy ölçümü başarısız: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        finally:
            if temp_image_path and os.path.exists(temp_image_path):
                os.remove(temp_image_path)

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

        try:
            plant = Plant.objects.get(id=plant_id)
        except Plant.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Bitki bulunamadı."
            }, status=status.HTTP_404_NOT_FOUND)

        temp_image_path = None
        try:
            import requests

            response = requests.get(image_url, stream=True, timeout=15)
            response.raise_for_status()

            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        tmp.write(chunk)
                temp_image_path = tmp.name

            result = predict_plant_species(image_path=temp_image_path)

            AnalysisResult.objects.create(
                plant=plant,
                species_prediction=result["predicted_species"],
                confidence=result["confidence"],
                health_status="unknown"
            )

            return Response({
                "status": "success",
                "data": {
                    "plant_id": plant.id,
                    "plant_species": result["predicted_species"],
                    "confidence": result["confidence"],
                    "top_predictions": result["top_predictions"],
                    "model_version": result["model_version"]
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": "error",
                "message": f"Tür tespiti başarısız: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        finally:
            if temp_image_path and os.path.exists(temp_image_path):
                os.remove(temp_image_path)

class GetAIAnalysisResultView(APIView):
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

        temp_image_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                for chunk in image_file.chunks():
                    tmp.write(chunk)
                temp_image_path = tmp.name

            result = predict_plant_species(image_path=temp_image_path)

            return Response({
                "status": "success",
                "data": {
                    "plant": result["predicted_species"],
                    "confidence": result["confidence"],
                    "top_predictions": result["top_predictions"],
                    "model_version": result["model_version"]
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": "error",
                "message": f"Tür tespiti başarısız: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        finally:
            if temp_image_path and os.path.exists(temp_image_path):
                os.remove(temp_image_path)


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