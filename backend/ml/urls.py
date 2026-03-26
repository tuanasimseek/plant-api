from django.urls import path
from .views import (
    StateMachineConfigView,
    UpdateStateMachineConfigView,
    GetLatestDecisionMechanismView,
    GetSimulationParamsView,
    SendSimulationResultsView,
    GetSimulationResultsView,
    EvaluateOptimalDecisionView,
    SaveOptimalDecisionView,
    SendDigitalTwinStatusView,
    GetDigitalTwinStatusView,
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
    path('digital-twin/status', SendDigitalTwinStatusView.as_view(), name='send-twin'),
    path('digital-twin/status', GetDigitalTwinStatusView.as_view(), name='get-twin'),
    path('optimization/best-config', SaveBestOptimizationConfigView.as_view(), name='best-config'),
]