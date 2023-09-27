from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.views import UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/', include(router.urls)),
    path('crud_user/', UserViewSet.as_view({'get': 'crud_user_form'}), name='crud_user_form'),
    path("", include("health_check.urls")),
]
