from django.contrib import admin
from .models import SensorReading, WateringHistory

admin.site.register(SensorReading)
admin.site.register(WateringHistory)