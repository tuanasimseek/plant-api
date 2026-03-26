from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("users.urls")),
    path("api/", include("plants.urls")),
    path("api/", include("pots.urls")),
    path("api/", include("sensors.urls")),
    path("api/", include("notifications.urls")),
    path("api/", include("ai.urls")),
    path("api/", include("ml.urls")),
     path("api/", include("devices.urls")),
]