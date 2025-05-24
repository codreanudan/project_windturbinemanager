from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import  api_dashboard_view, WindTurbineViewSet

router = DefaultRouter()
router.register(r'turbines', WindTurbineViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', api_dashboard_view, name='api-dashboard'),
]