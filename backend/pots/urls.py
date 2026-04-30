from django.urls import path
from .views import (
    VerifyPotQRView,
    RegisterPotDeviceView,
    ActivatePotView,
    AssignPlantToPotView,
    PotListView,
    PotDetailView,
    MyPotsView,
)

urlpatterns = [
    path('pots/verify/<str:device_code>', VerifyPotQRView.as_view(), name='verify-pot'),
    path('pots/register', RegisterPotDeviceView.as_view(), name='register-pot'),
    path('pots/activate', ActivatePotView.as_view(), name='activate-pot'),
    path('pots/my', MyPotsView.as_view(), name='my-pots'),  
    path('pots', PotListView.as_view(), name='pot-list'),
    path('pots/<int:pot_id>', PotDetailView.as_view(), name='pot-detail'),
    path('pots/<int:pot_id>/plant', AssignPlantToPotView.as_view(), name='assign-plant'),
]