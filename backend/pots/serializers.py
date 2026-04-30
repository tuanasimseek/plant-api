from rest_framework import serializers
from .models import Pot
from plants.serializers import PlantSerializer
from sensors.models import SensorReading


class PotSerializer(serializers.ModelSerializer):
    plant = PlantSerializer(read_only=True)
    device_code = serializers.CharField(source='device.device_code', read_only=True)  # device_id → device_code
    device_db_id = serializers.IntegerField(source='device.id', read_only=True)        # eklendi
    device_status = serializers.CharField(source='device.status', read_only=True)
    last_update = serializers.DateTimeField(source='updated_at', read_only=True)

    class Meta:
        model = Pot
        fields = (
            'id', 'device_db_id', 'device_code', 'plant', 'nickname',
            'is_active', 'placement_status', 'device_status', 'last_update'
        )


class PotDetailSerializer(serializers.ModelSerializer):
    plant = PlantSerializer(read_only=True)
    device_code = serializers.CharField(source='device.device_code', read_only=True)  # düzeltildi
    device_db_id = serializers.IntegerField(source='device.id', read_only=True)        # eklendi
    device_status = serializers.CharField(source='device.status', read_only=True)
    last_reading = serializers.SerializerMethodField()
    last_update = serializers.DateTimeField(source='updated_at', read_only=True)

    class Meta:
        model = Pot
        fields = (
            'id', 'device_db_id', 'device_code', 'plant', 'nickname',
            'is_active', 'placement_status', 'device_status',
            'last_reading', 'last_update'
        )

    def get_last_reading(self, obj):
        reading = SensorReading.objects.filter(pot=obj).order_by('-recorded_at').first()
        if reading:
            return {
                "temperature": reading.temperature,
                "humidity": reading.humidity,
                "soil_moisture": reading.soil_moisture,
                "light": reading.light,
                "water_level": reading.water_level,
            }
        return None


class MyPotSerializer(serializers.ModelSerializer):
    plant_name = serializers.SerializerMethodField()
    device_code = serializers.SerializerMethodField()   # device_id → device_code
    device_db_id = serializers.SerializerMethodField()  # eklendi
    device_status = serializers.SerializerMethodField()
    water_level = serializers.SerializerMethodField()
    last_update = serializers.DateTimeField(source='updated_at', read_only=True)

    class Meta:
        model = Pot
        fields = [
            'id',
            'nickname',
            'plant_name',
            'device_db_id',    # eklendi
            'device_code',     # device_id → device_code
            'device_status',
            'is_active',
            'placement_status',
            'water_level',
            'created_at',
            'updated_at',
            'last_update',
        ]

    def get_plant_name(self, obj):
        return obj.plant.name if obj.plant else None

    def get_device_code(self, obj):                          # get_device_id → get_device_code
        return obj.device.device_code if obj.device else None

    def get_device_db_id(self, obj):                         # eklendi
        return obj.device.id if obj.device else None

    def get_device_status(self, obj):
        if not obj.device:
            return None
        return {
            "status": obj.device.status,
            "is_watering": obj.device.is_watering,
            "battery_level": obj.device.battery_level,
            "last_seen_at": obj.device.last_seen_at,
        }

    def get_water_level(self, obj):
        reading = SensorReading.objects.filter(pot=obj).order_by('-recorded_at').first()
        return reading.water_level if reading else None