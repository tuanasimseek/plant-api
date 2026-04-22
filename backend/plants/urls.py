from django.urls import path
from .views import PlantListView, PlantCategoryListView, PlantSearchView, PlantDetailView


urlpatterns = [
    path('plants', PlantListView.as_view(), name='plant-list'),
    path('plants/categories', PlantCategoryListView.as_view(), name='plant-categories'),
    path('plants/search', PlantSearchView.as_view(), name='plant-search'),
    path('plants/<int:plant_id>', PlantDetailView.as_view(), name='plant-detail'),
]
