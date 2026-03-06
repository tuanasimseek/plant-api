from django.urls import path
from .views import(
    plant_list,
    plant_detail,
    plant_categories,
    pot_list_create,
    pot_detail_patch,
    pot_latest_reading,
    reading_create_device,
    pot_command_create,
    pot_pending_commands_device,
    command_update_status_device,
) 

urlpatterns = [
    #plants
    path("plants/", plant_list),
    path("plants/categories/", plant_categories),
    path("plants/<int:plant_id>/", plant_detail),
    
    #pots
    path("pots/", pot_list_create),
    path("pots/<int:pot_id>/", pot_detail_patch),
    path("pots/<int:pot_id>/latest/", pot_latest_reading),

    #readings
    path("readings/", reading_create_device),

    #commands
    path("pots/<int:pot_id>/command/", pot_command_create),
    path("pots/<int:pot_id>/pending-commands/", pot_pending_commands_device),
    path("commands/<int:command_id>/status/", command_update_status_device),

]