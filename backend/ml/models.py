from django.db import models
from pots.models import Pot


class StateMachineConfig(models.Model):
    soil_moisture_min = models.FloatField(default=30)
    soil_moisture_max = models.FloatField(default=65)
    temperature_min = models.FloatField(default=18)
    temperature_max = models.FloatField(default=28)
    light_min = models.FloatField(default=200)
    light_max = models.FloatField(default=800)
    moisture_threshold = models.FloatField(default=30)
    watering_duration_ms = models.IntegerField(default=5000)
    sleep_interval_min = models.IntegerField(default=15)
    auto_mode = models.BooleanField(default=True)
    version = models.CharField(max_length=20, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Config v{self.version}"


class SimulationResult(models.Model):
    GROWTH_STAGE_CHOICES = (
        ('healthy_growth', 'Healthy Growth'),
        ('stressed_growth', 'Stressed Growth'),
        ('critical', 'Critical'),
    )

    pot = models.ForeignKey(Pot, on_delete=models.CASCADE, related_name='simulation_results')
    
    # Yeni Unity field'ları
    health_score = models.FloatField(blank=True, null=True)        # 0.0 - 1.0
    water_level = models.FloatField(blank=True, null=True)
    stress_level = models.FloatField(blank=True, null=True)        # 0.0 - 1.0
    growth_stage = models.CharField(
        max_length=20, 
        choices=GROWTH_STAGE_CHOICES, 
        blank=True, null=True
    )
    is_dead = models.BooleanField(default=False)
    total_pots = models.IntegerField(blank=True, null=True)
    
    # simulation_time artık Unity'den geliyor, auto_now_add kaldırıldı
    simulation_time = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Simulation {self.id} - Pot {self.pot_id}"


class OptimalDecision(models.Model):
    ADJUSTMENT_CHOICES = (
        ('increase', 'Increase'),
        ('decrease', 'Decrease'),
        ('none', 'None'),
    )

    pot = models.ForeignKey(Pot, on_delete=models.CASCADE, related_name='optimal_decisions')
    watering_needed = models.BooleanField(default=False)
    recommended_watering_ml = models.FloatField(blank=True, null=True)
    light_adjustment = models.CharField(max_length=10, choices=ADJUSTMENT_CHOICES, default='none')
    temperature_adjustment = models.CharField(max_length=10, choices=ADJUSTMENT_CHOICES, default='none')
    confidence = models.FloatField(blank=True, null=True)
    model_version = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Decision {self.id} - Pot {self.pot_id}"


class DigitalTwinStatus(models.Model):
    SIMULATION_STATE_CHOICES = (
        ('stable', 'Stable'),
        ('growing', 'Growing'),
        ('stressed', 'Stressed'),
        ('critical', 'Critical'),
    )

    pot = models.OneToOneField(Pot, on_delete=models.CASCADE, related_name='digital_twin')
    health_score = models.FloatField(blank=True, null=True)
    growth_stage = models.CharField(max_length=50, blank=True, null=True)
    predicted_height_cm = models.FloatField(blank=True, null=True)
    water_status = models.CharField(max_length=50, blank=True, null=True)
    simulation_state = models.CharField(max_length=20, choices=SIMULATION_STATE_CHOICES, default='stable')
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"DigitalTwin - Pot {self.pot_id}"