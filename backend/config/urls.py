from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

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

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)