from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .api_views import (
    RegisterAPIView,
    LoginAPIView,
    CurrentUserAPIView,
    DashboardSummaryAPIView,
    TemporarySetupAPIView,
    DoctorViewSet,
    AppointmentSlotViewSet,
    AppointmentViewSet,
    PatientViewSet,
)

router = DefaultRouter()

router.register(r'doctors', DoctorViewSet, basename='doctor')
router.register(r'slots', AppointmentSlotViewSet, basename='slot')
router.register(r'appointments', AppointmentViewSet, basename='appointment')
router.register(r'patients', PatientViewSet, basename='patient')

urlpatterns = [
    path('auth/', include('rest_framework.urls')),

    path('register/', RegisterAPIView.as_view(), name='api_register'),
    path('login/', LoginAPIView.as_view(), name='api_login'),
    path('me/', CurrentUserAPIView.as_view(), name='api_me'),
    path('dashboard-summary/', DashboardSummaryAPIView.as_view(), name='dashboard_summary'),
    path('temporary-setup/', TemporarySetupAPIView.as_view(), name='temporary_setup'),

    path('', include(router.urls)),
]