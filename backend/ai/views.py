import os
import tempfile

from django.db.models import Q
from django.utils import timezone

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser

from .models import PlantImage, AnalysisResult, OptimalDecision
from .ml_service import (
    predict_plant_height,
    predict_plant_species,
    predict_plant_health,
    predict_simulation,
    predict_ml004_decision,
)

from ml.models import SimulationResult
from plants.models import Plant
from pots.models import Pot
from sensors.models import SensorReading


def get_user_pot_for_plant(plant, user):
    return Pot.objects.filter(
        Q(plant=plant) & (Q(owner=user) | Q(allowed_users=user))
    ).distinct().first()


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

        image_file = request.FILES.get("image")

        if not image_file:
            return Response({
                "status": "error",
                "message": "Görüntü zorunludur."
            }, status=status.HTTP_400_BAD_REQUEST)

        plant_image = PlantImage.objects.create(
            plant=plant,
            image=image_file,
            source=request.data.get("source"),
            captured_at=request.data.get("captured_at"),
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
        plant_id = request.data.get("plant_id")
        image_url = request.data.get("image_url")

        if not plant_id:
            return Response({
                "status": "error",
                "message": "plant_id zorunludur."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            plant = Plant.objects.get(id=plant_id)
        except Plant.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Bitki bulunamadı."
            }, status=status.HTTP_404_NOT_FOUND)

        pot = get_user_pot_for_plant(plant, request.user)

        if not pot:
            return Response({
                "status": "error",
                "message": "Bu bitkiye bağlı saksı bulunamadı."
            }, status=status.HTTP_404_NOT_FOUND)

        if not image_url:
            last_image = PlantImage.objects.filter(
                plant=plant
            ).order_by("-uploaded_at").first()

            if not last_image:
                return Response({
                    "status": "error",
                    "message": "Bu bitkiye ait görüntü bulunamadı. Lütfen önce görüntü yükleyin."
                }, status=status.HTTP_404_NOT_FOUND)

            image_url = request.build_absolute_uri(last_image.image.url)

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

            health_result = predict_plant_health(image_path=temp_image_path)

            result = AnalysisResult.objects.create(
                pot=pot,
                plant=plant,
                health_status=health_result["health_status"],
                disease_detected=health_result["disease_detected"],
                disease_name=health_result["disease_name"],
                confidence=health_result["confidence"],
            )

            return Response({
                "status": "success",
                "data": {
                    "pot_id": pot.id,
                    "plant_id": plant.id,
                    "health_status": health_result["health_status"],
                    "disease_detected": health_result["disease_detected"],
                    "disease_name": health_result["disease_name"],
                    "confidence": health_result["confidence"],
                    "top_predictions": health_result.get("top_predictions"),
                    "model_version": health_result.get("model_version"),
                    "analysis_id": result.id,
                    "image_url": image_url,
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
        plant_id = request.data.get("plant_id")
        image_url = request.data.get("image_url")
        reference_object_cm = request.data.get("reference_object_cm", 9)

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

        pot = get_user_pot_for_plant(plant, request.user)

        if not pot:
            return Response({
                "status": "error",
                "message": "Bu bitkiye bağlı saksı bulunamadı."
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

            result = predict_plant_height(
                image_path=temp_image_path,
                reference_object_cm=float(reference_object_cm)
            )

            analysis = AnalysisResult.objects.create(
                pot=pot,
                plant=plant,
                estimated_height_cm=result["estimated_height_cm"],
                confidence=result["confidence"],
                health_status="unknown"
            )

            return Response({
                "status": "success",
                "data": {
                    "pot_id": pot.id,
                    "plant_id": plant.id,
                    "estimated_height_cm": result["estimated_height_cm"],
                    "confidence": result["confidence"],
                    "model_version": result.get("model_version"),
                    "analysis_id": analysis.id,
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": "error",
                "message": f"Boy ölçümü başarısız: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        finally:
            if temp_image_path and os.path.exists(temp_image_path):
                os.remove(temp_image_path)


class MeasurePlantHeightLiveView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        image_file = request.FILES.get("image")
        reference_object_cm = request.data.get("reference_object_cm", 9)

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
        plant_id = request.data.get("plant_id")
        current_image_url = request.data.get("current_image_url")
        previous_image_url = request.data.get("previous_image_url")

        if not plant_id or not current_image_url or not previous_image_url:
            return Response({
                "status": "error",
                "message": "plant_id, current_image_url ve previous_image_url zorunludur."
            }, status=status.HTTP_400_BAD_REQUEST)

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
        plant_id = request.data.get("plant_id")
        image_url = request.data.get("image_url")

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

        pot = get_user_pot_for_plant(plant, request.user)

        if not pot:
            return Response({
                "status": "error",
                "message": "Bu bitkiye bağlı saksı bulunamadı."
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

            analysis = AnalysisResult.objects.create(
                pot=pot,
                plant=plant,
                species_prediction=result["predicted_species"],
                confidence=result["confidence"],
                health_status="unknown"
            )

            return Response({
                "status": "success",
                "data": {
                    "pot_id": pot.id,
                    "plant_id": plant.id,
                    "plant_species": result["predicted_species"],
                    "confidence": result["confidence"],
                    "top_predictions": result.get("top_predictions"),
                    "model_version": result.get("model_version"),
                    "analysis_id": analysis.id,
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
        pot = Pot.objects.filter(
            Q(id=pot_id) & (Q(owner=request.user) | Q(allowed_users=request.user))
        ).distinct().first()

        if not pot:
            return Response({
                "status": "error",
                "message": "Saksı bulunamadı."
            }, status=status.HTTP_404_NOT_FOUND)

        result = AnalysisResult.objects.filter(
            pot=pot
        ).order_by("-analyzed_at").first()

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
        ).order_by("-analyzed_at").values(
            "analyzed_at",
            "health_status",
            "disease_name",
            "estimated_height_cm"
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
        image_file = request.FILES.get("image")

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
                    "top_predictions": result.get("top_predictions"),
                    "model_version": result.get("model_version")
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
        question = request.data.get("question")

        if not question:
            return Response({
                "status": "error",
                "message": "Soru zorunludur."
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "status": "success",
            "data": {
                "answer": "Yaprakların sararması genellikle fazla sulama veya düşük ışık seviyesinden kaynaklanabilir. Toprak nem seviyesini kontrol etmeniz önerilir."
            }
        }, status=status.HTTP_200_OK)


class GetSimulationResultsView(APIView):
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

        sensor = SensorReading.objects.filter(
            pot=pot
        ).order_by("-recorded_at").first()

        if not sensor:
            return Response({
                "status": "error",
                "message": "Bu saksıya ait sensör verisi bulunamadı."
            }, status=status.HTTP_404_NOT_FOUND)

        plant = pot.plant

        if not plant:
            return Response({
                "status": "error",
                "message": "Bu saksıya ait bitki bulunamadı."
            }, status=status.HTTP_404_NOT_FOUND)

        last_watering_day = (timezone.now() - sensor.recorded_at).days
        plant_age_days = (timezone.now().date() - plant.created_at.date()).days

        try:
            result = predict_simulation(
                temperature=float(sensor.temperature),
                humidity=float(sensor.humidity),
                soil_moisture=float(sensor.soil_moisture),
                light=float(sensor.light),
                water_level=float(sensor.water_level),
                ph=float(getattr(sensor, "ph", 7.0)),
                last_watering_day=last_watering_day,
                plant_age_days=plant_age_days,
            )
        except Exception as e:
            return Response({
                "status": "error",
                "message": f"Simülasyon başarısız: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        SimulationResult.objects.create(
            pot=pot,
            predicted_growth_cm=result["predicted_growth_cm"],
            recommended_watering_ml=result["recommended_watering_ml"],
            confidence=result["confidence"],
            simulation_time=timezone.now(),
        )

        history = SimulationResult.objects.filter(
            pot=pot
        ).order_by("-simulation_time")[:10]

        return Response({
            "status": "success",
            "data": {
                "pot_id": pot.id,
                "simulation_results": [
                    {
                        "predicted_growth_cm": s.predicted_growth_cm,
                        "recommended_watering_ml": s.recommended_watering_ml,
                        "confidence": s.confidence,
                        "simulation_time": s.simulation_time,
                    }
                    for s in history
                ]
            }
        }, status=status.HTTP_200_OK)


class GetML004AnalysisView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        pot_id = request.data.get("pot_id")
        soil_moisture = request.data.get("soil_moisture")
        temperature = request.data.get("temperature")
        light = request.data.get("light")
        air_humidity = request.data.get("air_humidity")

        if not all([pot_id, soil_moisture, temperature, light, air_humidity]):
            return Response({
                "status": "error",
                "message": "pot_id, soil_moisture, temperature, light ve air_humidity zorunludur."
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
            result = predict_ml004_decision(
                soil_moisture=float(soil_moisture),
                temperature=float(temperature),
                light=float(light),
                air_humidity=float(air_humidity),
            )
        except Exception as e:
            return Response({
                "status": "error",
                "message": f"ML-004 analizi başarısız: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        OptimalDecision.objects.create(
            pot=pot,
            watering_needed=result["watering_needed"],
            recommended_watering_ml=result["recommended_watering_ml"],
            light_adjustment=result["light_adjustment"],
            temperature_adjustment=result["temperature_adjustment"],
            confidence=result["confidence"],
        )

        return Response({
            "status": "success",
            "data": result
        }, status=status.HTTP_200_OK)