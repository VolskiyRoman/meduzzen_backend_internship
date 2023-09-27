from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.views import UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/', include(router.urls)),
    path('create_user/', UserViewSet.as_view({'get': 'create_user_form'}), name='create_user_form'),
    path("", include("health_check.urls")),
]
