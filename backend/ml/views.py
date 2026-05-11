from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .models import StateMachineConfig, SimulationResult, OptimalDecision, DigitalTwinStatus
from .serializers import (
    StateMachineConfigSerializer,
    SimulationResultSerializer,
    OptimalDecisionSerializer,
    DigitalTwinStatusSerializer,
)
from pots.models import Pot
from django.utils import timezone
from ai.ml_service import predict_ml004_decision

class StateMachineConfigView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        config = StateMachineConfig.objects.first()
        if not config:
            return Response({
                "status": "error",
                "message": "Config bulunamadı."
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = StateMachineConfigSerializer(config)
        return Response({
            "status": "success",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def patch(self, request):
        config = StateMachineConfig.objects.first()
        if not config:
            config = StateMachineConfig.objects.create()

        serializer = StateMachineConfigSerializer(config, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": "success",
                "message": "State machine configuration updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "status": "error",
            "message": "Geçersiz veri.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class GetLatestDecisionMechanismView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        config = StateMachineConfig.objects.order_by('-updated_at').first()
        if not config:
            return Response({
                "status": "error",
                "message": "Config bulunamadı."
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = StateMachineConfigSerializer(config)
        return Response({
            "status": "success",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class GetSimulationParamsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "status": "success",
            "data": {
                "growth_factor": 1.2,
                "moisture_effect": 0.8,
                "light_effect": 0.9,
                "temperature_effect": 0.7,
                "update_interval_seconds": 60
            }
        }, status=status.HTTP_200_OK)


class SendSimulationResultsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        pot_id = request.data.get('pot_id')
        simulation_time = request.data.get('simulation_time')
        total_pots = request.data.get('total_pots')
        results = request.data.get('results', [])

        if not pot_id:
            return Response({
                "status": "error",
                "message": "pot_id gerekli."
            }, status=status.HTTP_400_BAD_REQUEST)

        if not results:
            return Response({
                "status": "error",
                "message": "results listesi boş olamaz."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            pot = Pot.objects.get(id=pot_id)
        except Pot.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Saksı bulunamadı."
            }, status=status.HTTP_404_NOT_FOUND)

        saved = []
        for item in results:
            result = SimulationResult.objects.create(
                pot=pot,
                health_score=item.get('health_score'),
                water_level=item.get('water_level'),
                stress_level=item.get('stress_level'),
                growth_stage=item.get('growth_stage'),
                is_dead=item.get('is_dead', False),
                total_pots=total_pots,
                simulation_time=simulation_time,  # ISO string Django otomatik parse eder
            )
            saved.append(result)

        return Response({
            "status": "success",
            "message": "Simulation results saved successfully"
        }, status=status.HTTP_201_CREATED)


class GetSimulationResultsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pot_id):
        try:
            pot = Pot.objects.get(id=pot_id)
        except Pot.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Saksı bulunamadı."
            }, status=status.HTTP_404_NOT_FOUND)

        results = SimulationResult.objects.filter(pot=pot).order_by('-simulation_time')
        serializer = SimulationResultSerializer(results, many=True)

        return Response({
            "status": "success",
            "data": {
                "pot_id": pot.id,
                "simulation_results": serializer.data
            }
        }, status=status.HTTP_200_OK)


class EvaluateOptimalDecisionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        pot_id = request.data.get('pot_id')
        soil_moisture = request.data.get('soil_moisture')
        temperature = request.data.get('temperature')
        light = request.data.get('light')
        air_humidity = request.data.get('air_humidity')

        if not pot_id:
            return Response({
                "status": "error",
                "message": "pot_id gerekli."
            }, status=status.HTTP_400_BAD_REQUEST)

        if soil_moisture is None or temperature is None or light is None or air_humidity is None:
            return Response({
                "status": "error",
                "message": "soil_moisture, temperature, light ve air_humidity gerekli."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            pot = Pot.objects.get(id=pot_id)
        except Pot.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Saksı bulunamadı."
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            result = predict_ml004_decision(
                soil_moisture=float(soil_moisture),
                temperature=float(temperature),
                light=float(light),
                air_humidity=float(air_humidity)
            )
        except Exception as e:
            return Response({
                "status": "error",
                "message": f"ML-004 karar analizi başarısız: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        OptimalDecision.objects.create(
            pot=pot,
            watering_needed=result["watering_needed"],
            recommended_watering_ml=result["recommended_watering_ml"],
            light_adjustment=result["light_adjustment"],
            temperature_adjustment=result["temperature_adjustment"],
            confidence=result["confidence"],
            model_version="ML-004"
        )

        return Response({
            "status": "success",
            "data": {
                "watering_needed": result["watering_needed"],
                "recommended_watering_ml": result["recommended_watering_ml"],
                "light_adjustment": result["light_adjustment"],
                "temperature_adjustment": result["temperature_adjustment"],
                "confidence": result["confidence"]
            }
        }, status=status.HTTP_200_OK)


class SaveOptimalDecisionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        pot_id = request.data.get('pot_id')

        if not pot_id:
            return Response({
                "status": "error",
                "message": "pot_id gerekli."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            pot = Pot.objects.get(id=pot_id)
        except Pot.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Saksı bulunamadı."
            }, status=status.HTTP_404_NOT_FOUND)

        decision = OptimalDecision.objects.create(
            pot=pot,
            watering_needed=request.data.get('watering_needed', False),
            recommended_watering_ml=request.data.get('recommended_watering_ml'),
            light_adjustment=request.data.get('light_adjustment', 'none'),
            temperature_adjustment=request.data.get('temperature_adjustment', 'none'),
            confidence=request.data.get('confidence'),
        )

        serializer = OptimalDecisionSerializer(decision)
        return Response({
            "status": "success",
            "message": "Optimal decision saved successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)


class DigitalTwinStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        pot_id = request.query_params.get('pot_id')

        if not pot_id:
            return Response({
                "status": "error",
                "message": "pot_id gerekli."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            pot = Pot.objects.get(id=pot_id)
        except Pot.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Saksı bulunamadı."
            }, status=status.HTTP_404_NOT_FOUND)

        twin = DigitalTwinStatus.objects.filter(pot=pot).first()
        if not twin:
            return Response({
                "status": "error",
                "message": "Digital twin status bulunamadı."
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = DigitalTwinStatusSerializer(twin)
        return Response({
            "status": "success",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request):
        pot_id = request.data.get('pot_id')

        if not pot_id:
            return Response({
                "status": "error",
                "message": "pot_id gerekli."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            pot = Pot.objects.get(id=pot_id)
        except Pot.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Saksı bulunamadı."
            }, status=status.HTTP_404_NOT_FOUND)

        twin, created = DigitalTwinStatus.objects.update_or_create(
            pot=pot,
            defaults={
                'health_score': request.data.get('health_score'),
                'growth_stage': request.data.get('growth_stage'),
                'predicted_height_cm': request.data.get('predicted_height_cm'),
                'water_status': request.data.get('water_status'),
                'simulation_state': request.data.get('simulation_state', 'stable'),
            }
        )

        serializer = DigitalTwinStatusSerializer(twin)
        return Response({
            "status": "success",
            "message": "Digital twin status saved successfully" if created else "Digital twin status updated successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class SaveBestOptimizationConfigView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        pot_id = request.data.get('pot_id')

        if not pot_id:
            return Response({
                "status": "error",
                "message": "pot_id gerekli."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            pot = Pot.objects.get(id=pot_id)
        except Pot.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Saksı bulunamadı."
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            optimal_duration = float(request.data.get('optimal_watering_duration', 5))
        except (TypeError, ValueError):
            return Response({
                "status": "error",
                "message": "optimal_watering_duration sayısal olmalı."
            }, status=status.HTTP_400_BAD_REQUEST)

        decision = OptimalDecision.objects.create(
            pot=pot,
            watering_needed=True,
            recommended_watering_ml=optimal_duration * 50,
            light_adjustment='none',
            temperature_adjustment='none',
            confidence=request.data.get('optimization_score'),
            model_version=request.data.get('model_version'),
        )

        serializer = OptimalDecisionSerializer(decision)
        return Response({
            "status": "success",
            "message": "Best optimization configuration saved",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)