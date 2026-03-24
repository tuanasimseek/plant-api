from django.urls import path
from .views import (
    PotListView,
    PotActivateView,
    PotRegisterView,
    PotDetailView,
    AssignPlantToPotView,
    VerifyPotQRView,
)

urlpatterns = [
    path('pots/', PotListView.as_view(), name='pot-list'),
    path('pots/activate/', PotActivateView.as_view(), name='pot-activate'),
    path('pots/register/', PotRegisterView.as_view(), name='pot-register'),
    path('pots/<int:pot_id>/', PotDetailView.as_view(), name='pot-detail'),
    path('pots/<int:pot_id>/plant/', AssignPlantToPotView.as_view(), name='pot-assign-plant'),
    path('pots/verify/<str:device_id>/', VerifyPotQRView.as_view(), name='pot-verify'),
]