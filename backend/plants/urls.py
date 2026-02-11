from django.urls import path
from .views import plant_list

urlpatterns = [
    path("plants/", plant_list),
]