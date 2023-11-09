from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)
from rest_framework.routers import DefaultRouter

from actions.views import InvitationViewSet, RequestViewSet
from company.views import CompanyViewSet
from quiz_app.views import QuizManagementViewSet
from users import views

router = DefaultRouter()
router.register(r'companies', CompanyViewSet)
router.register(r'invite', InvitationViewSet)
router.register(r'request', RequestViewSet)
router.register(r'quizzes', QuizManagementViewSet)

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
    path('user/delete/<int:pk>/', views.UserDeleteView.as_view(), name='user-delete')
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
