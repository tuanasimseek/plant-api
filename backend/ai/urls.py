from django.urls import path
from .views import (
    UploadPlantImageView,
    AnalyzePlantImageView,
    MeasurePlantHeightView,
    MeasurePlantHeightLiveView,
    AnalyzeGrowthView,
    ClassifyPlantSpeciesView,
    GetAIAnalysisResultView,
    GetPlantHealthHistoryView,
    GuestAIScanView,
    MemberAIChatView,
)

urlpatterns = [
    path('plants/<int:plant_id>/image', UploadPlantImageView.as_view(), name='upload-image'),
    path('ai/analyze-plant', AnalyzePlantImageView.as_view(), name='analyze-plant'),
    path('ai/measure-height', MeasurePlantHeightView.as_view(), name='measure-height'),
    path('ai/measure-height-live', MeasurePlantHeightLiveView.as_view(), name='measure-height-live'),
    path('ai/analyze-growth', AnalyzeGrowthView.as_view(), name='analyze-growth'),
    path('ai/classify-plant-species', ClassifyPlantSpeciesView.as_view(), name='classify-species'),
    path('pots/<int:pot_id>/analysis', GetAIAnalysisResultView.as_view(), name='ai-analysis'),
    path('plants/<int:plant_id>/health-history', GetPlantHealthHistoryView.as_view(), name='health-history'),
    path('ai/guest-scan', GuestAIScanView.as_view(), name='guest-scan'),
    path('ai/member-chat', MemberAIChatView.as_view(), name='member-chat'),
    #path('ml/simulation-results/<int:pot_id>', GetSimulationResultsView.as_view(), name='simulation-results'),
    #path('ml/evaluate-optimal-decision', GetML004AnalysisView.as_view(), name='evaluate-optimal-decision'),
]