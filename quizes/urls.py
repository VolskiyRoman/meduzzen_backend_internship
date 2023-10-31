from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)
from rest_framework.routers import DefaultRouter

from actions.views import InvitationViewSet, RequestViewSet
from company.views import CompanyViewSet

router = DefaultRouter()
router.register(r'companies', CompanyViewSet)
router.register(r'invite', InvitationViewSet)
router.register(r'request', RequestViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        'api/schema/',
        SpectacularAPIView.as_view(),
        name='api-schema'
    ),
    path(
        'api/docs/',
        SpectacularSwaggerView.as_view(url_name='api-schema'),
        name='api-docs',
    ),
    path("", include("health_check.urls")),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('auth/', include('djoser.social.urls')),
    path('api/', include(router.urls)),
]
