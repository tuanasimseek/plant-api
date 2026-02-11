from rest_framework import serializers

class PlantSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    size_cm = serializers.IntegerField()
    image = serializers.CharField()
