from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import  api_dashboard_view, WindTurbineViewSet

router = DefaultRouter()
router.register(r'turbines', WindTurbineViewSet)
# router.register(r'turbines', WindTurbineViewSet, basename='turbine')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', api_dashboard_view, name='api-dashboard'),
    # path('', api_dashboard_view),
]