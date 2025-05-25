# urls.py - Updated to support both Django ORM and MongoDB
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import api_dashboard_view, WindTurbineViewSet, MongoWindTurbineViewSet

# Create separate routers for different backends
django_router = DefaultRouter()
django_router.register(r'turbines-django', WindTurbineViewSet, basename='turbine-django')

mongo_router = DefaultRouter()
mongo_router.register(r'turbines', MongoWindTurbineViewSet, basename='turbine-mongo')


urlpatterns = [
    # MongoDB-backed API (primary)
    path('', include(mongo_router.urls)),  # <-- Remove 'api/' prefix here
    
    # Django ORM-backed API (for compatibility)
    path('legacy/', include(django_router.urls)),
    
    # Dashboard
    path('dashboard/', api_dashboard_view, name='api-dashboard'),
    path('', api_dashboard_view, name='dashboard-home'),
    
    # Health check endpoint
    path('health/', MongoWindTurbineViewSet.as_view({'get': 'health'}), name='health-check'),
]
