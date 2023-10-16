from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from company.views import CompanyViewSet
from users.views import UserViewSet

router = DefaultRouter()
router.register(r'companies', CompanyViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path('crud_user/', UserViewSet.as_view({'get': 'crud_user_form'}), name='crud_user_form'),
    path("", include("health_check.urls")),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('auth/', include('djoser.social.urls')),
    path('api/', include(router.urls)),
]
