from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MongoWindTurbineViewSet, api_dashboard_view

router = DefaultRouter()
router.register(r'turbines', MongoWindTurbineViewSet, basename='mongo-turbine')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', api_dashboard_view, name='api-dashboard'),
]