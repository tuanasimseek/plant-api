from rest_framework import serializers
from .models import Plant,Pot,Reading,Command

class PlantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plant
        fields = "__all__"

class PotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pot
        fields = "__all__"
        read_only_fields = ["owner","device_token","created_at"]

class ReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reading
        fields = "__all__"

class CommandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Command
        fields = "__all__"    
        read_only_fields = ["status","created_at"]
        