from rest_framework import serializers
from .models import StateMachineConfig, SimulationResult, OptimalDecision, DigitalTwinStatus


class StateMachineConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = StateMachineConfig
        fields = (
            'id', 'soil_moisture_min', 'soil_moisture_max',
            'temperature_min', 'temperature_max',
            'light_min', 'light_max',
            'moisture_threshold', 'watering_duration_ms',
            'sleep_interval_min', 'auto_mode', 'version', 'updated_at'
        )


class SimulationResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimulationResult
        fields = (
            'id', 'predicted_growth_cm', 'recommended_watering_ml',
            'confidence', 'simulation_time', 'created_at'
        )


class OptimalDecisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = OptimalDecision
        fields = (
            'id', 'watering_needed', 'recommended_watering_ml',
            'light_adjustment', 'temperature_adjustment',
            'confidence', 'model_version', 'created_at'
        )


class DigitalTwinStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = DigitalTwinStatus
        fields = (
            'id', 'pot', 'health_score', 'growth_stage',
            'predicted_height_cm', 'water_status',
            'simulation_state', 'last_updated'
        )