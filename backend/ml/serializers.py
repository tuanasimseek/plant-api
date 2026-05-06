import json
from rest_framework import serializers
from .models import (
    StateMachineConfig,
    SimulationResult,
    OptimalDecision,
    DigitalTwinStatus
)


class StateMachineConfigSerializer(serializers.ModelSerializer):
    transitions_json = serializers.SerializerMethodField()

    class Meta:
        model = StateMachineConfig
        fields = (
            'id',
            'soil_moisture_min',
            'soil_moisture_max',
            'temperature_min',
            'temperature_max',
            'light_min',
            'light_max',
            'moisture_threshold',
            'watering_duration_ms',
            'sleep_interval_min',
            'auto_mode',
            'version',
            'updated_at',
            'transitions_json'
        )

    def get_transitions_json(self, obj):
        data = [
            {
                "from": "MONITORING",
                "to": "WATERING",
                "condition_param": "soil_moisture",
                "condition_op": "<",
                "condition_value": 40,
                "action": "pump_on",
                "action_duration": 6
            },
            {
                "from": "WATERING",
                "to": "MONITORING",
                "condition_param": "soil_moisture",
                "condition_op": ">=",
                "condition_value": 55,
                "action": "pump_off",
                "action_duration": 0
            }
        ]

        return json.dumps(data)


class SimulationResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimulationResult
        fields = (
            'id',
            'predicted_growth_cm',
            'recommended_watering_ml',
            'confidence',
            'simulation_time',
            'created_at'
        )


class OptimalDecisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = OptimalDecision
        fields = (
            'id',
            'watering_needed',
            'recommended_watering_ml',
            'light_adjustment',
            'temperature_adjustment',
            'confidence',
            'model_version',
            'created_at'
        )


class DigitalTwinStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = DigitalTwinStatus
        fields = (
            'id',
            'pot',
            'health_score',
            'growth_stage',
            'predicted_height_cm',
            'water_status',
            'simulation_state',
            'last_updated'
        )