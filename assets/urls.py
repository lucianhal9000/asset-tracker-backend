from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AssetStatsView, AssetViewSet, LocationViewSet, TelemetryView

router = DefaultRouter()
router.register(r'assets', AssetViewSet, basename='asset')
router.register(r'locations', LocationViewSet, basename='location')

urlpatterns = [
    path('assets/stats/', AssetStatsView.as_view(), name='asset-stats'),
    path('telemetry/', TelemetryView.as_view(), name='telemetry'),
    path('', include(router.urls)),
]