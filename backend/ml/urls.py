from django.urls import path
from .views import (
    StateMachineConfigView,
    GetLatestDecisionMechanismView,
    GetSimulationParamsView,
    SendSimulationResultsView,
    GetSimulationResultsView,
    EvaluateOptimalDecisionView,
    SaveOptimalDecisionView,
    DigitalTwinStatusView,
    SaveBestOptimizationConfigView,
)

urlpatterns = [
    path('state-machine/config', StateMachineConfigView.as_view(), name='state-machine-config'),
    path('state-machine/config/latest', GetLatestDecisionMechanismView.as_view(), name='latest-config'),
    path('simulation/params', GetSimulationParamsView.as_view(), name='simulation-params'),
    path('simulation/results', SendSimulationResultsView.as_view(), name='send-simulation'),
    path('ml/simulation-results/<int:pot_id>', GetSimulationResultsView.as_view(), name='get-simulation'),
    path('ml/evaluate-optimal-decision', EvaluateOptimalDecisionView.as_view(), name='evaluate-decision'),
    path('ml/save-optimal-decision', SaveOptimalDecisionView.as_view(), name='save-decision'),
    path('digital-twin/status', DigitalTwinStatusView.as_view(), name='digital-twin-status'),
    path('optimization/best-config', SaveBestOptimizationConfigView.as_view(), name='best-config'),
]