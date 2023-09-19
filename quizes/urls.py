from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("health_check.urls")),  # Use your app's name "health_check"
]
